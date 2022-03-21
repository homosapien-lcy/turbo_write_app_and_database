import time

from sklearn.cluster import MiniBatchKMeans
from python_utils.sentenceEmbeddingUtils import *
from python_utils.markovDictUtils import *

from RDRPOSTagger import *
RDRPOSTagger = RDRPOSTagger()
RDRPOSTagger.englishSetup()


def runGenerateRDRTag(sentence):
    return generateRDRTags(RDRPOSTagger, sentence)


processing_batch_size = 10000
paragraph_length_cut = 20
sentence_length_cut = 5

section_text_fn = sys.argv[1]
idf_info_fn = sys.argv[2]
subject = sys.argv[3]
trained_model_file = sys.argv[4]
phrase_mode_option = sys.argv[5]
output_markov_dict_prefix = sys.argv[6]

output_markov_dict_folder = output_markov_dict_prefix + '/'

fast_text_path = "fasttext"
fasttext_model_folder = fasttext_folder + \
    "result/fasttext_model_dim_150_min_df_100/"
bin_file_tail = "_fasttext_model.bin"
vec_file_tail = "_fasttext_model.vec"

model_bin = fasttext_model_folder + subject + bin_file_tail
model_vec = fasttext_model_folder + subject + vec_file_tail

idf_info_fn = idf_info_fn.lower()
# case of using no idf weighting
if idf_info_fn == "none":
    print("use no idf weighting")
    # initialize embedding
    sentence_database_embedding = SentenceEmbedding()
    print("embedding has been initilized")
    # set the option for using idf weighting
    IDF_weighting_option = False
    IDF_prefix = "Unweighted"
else:
    # load the idf model file
    idf_info = loadPythonObject(idf_info_fn)
    print("finish loading idf info")
    # initialize embedding
    sentence_database_embedding = SentenceEmbedding(idf_info)
    print("embedding has been initilized")
    # set the option for using idf weighting
    IDF_weighting_option = True
    IDF_prefix = "IDFWeighted"

default_IDF_weight_option = 0
spell_correct_option = False

# load the kmeans model
mini_batch_kmeans = loadPythonObject(trained_model_file)
print("loading pre-trained model")

section_text_file = open(section_text_fn, 'r')
merged_markov_dict_all = []
for batch_index, paragraph_batch in enumerate(chunked(section_text_file, processing_batch_size)):
    print("processing batch", batch_index)
    # if paragraph < paragraph_length_cut (invalid paragraph), remove
    # ---------------------------------------------------------------------------------------
    start = time.time()
    paragraph_batch = filterStringsTooShort(
        paragraph_batch, paragraph_length_cut)
    end = time.time()
    print("filter string for this batch took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    '''
    generate cluster index for each paragraph, with following steps
    1 split into sentences
    2 filter sentences thats shorter than sentence_length_cut (aka invalid), use filterStringsTooShort
    3 RDR tag each sentence and extract relation_VP, use extractPatternAndJoinNeighbor(sentence, target_pattern, tag_operator)
    4 embed with SentenceEmbedding class
    5 use Kmeans to map to cluster
    6 generate markov chain counts
    above steps in efficient way:
    (1) step 1, 2, 3 (MP)
    (2) pool together the phrases and get fasttext embedding (SP getEmbeddingLUTFromFastText)
    (3) step 4, 5, 6 (MP)
    '''
    # (1)
    # ---------------------------------------------------------------------------------------
    start = time.time()
    phrase_batch = paragraphToPatternPhraseArrSP(paragraph_batch, sentence_length_cut,
                                                 relation_VP_pattern, runGenerateRDRTag,
                                                 extractPatternOperator=extractPatternAndJoinNeighbor,
                                                 phrase_mode=phrase_mode_option)
    end = time.time()
    print("step (1) took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # (2)
    # ---------------------------------------------------------------------------------------
    start = time.time()
    batch_cur_embedding_LUT = getEmbeddingLUTFromFastText(
        flatten(phrase_batch), fast_text_path, model_bin)
    end = time.time()
    print("step (2) took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # (3)
    # ---------------------------------------------------------------------------------------
    start = time.time()

    def arr_embedding_operator(s_arr): return sentence_database_embedding.embedSentenceWithEmbeddingLUTArrSP(s_arr,
                                                                                                             batch_cur_embedding_LUT,
                                                                                                             weighted_by_IDF=IDF_weighting_option,
                                                                                                             default_IDF_weight=default_IDF_weight_option,
                                                                                                             spell_correct=spell_correct_option)
    batch_markov_dict_arr = phraseSequenceToMarkovDictionaryArrSP(
        phrase_batch, arr_embedding_operator, mini_batch_kmeans)
    end = time.time()
    print("step (3) took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # merge the collected markov chain dictionary using reduce
    # do this for each batch for saving memory
    # ---------------------------------------------------------------------------------------
    start = time.time()
    batch_merged_markov_dict = mergeMarkovDictArr(batch_markov_dict_arr)
    merged_markov_dict_all.append(batch_merged_markov_dict)
    end = time.time()
    print("merge dictionaries in this batch took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
start = time.time()
# merge the collected markov chain dictionary using reduce
# do this for each batch for saving memory
total_markov_dict = mergeMarkovDictArr(merged_markov_dict_all)
# normalize markov dictionary
normalized_total_markov_dict = normalizeMarkovDict(total_markov_dict)
end = time.time()
print("merge and normalize dictionaries took", end-start, "seconds")
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
start = time.time()
print("normalized_total_markov_dict:", normalized_total_markov_dict)
checkAndCreateFolder(output_markov_dict_folder)
savePythonObject(total_markov_dict, output_markov_dict_folder + output_markov_dict_prefix +
                 "_" + IDF_prefix + "_" + phrase_mode_option + "_unnormalized.pkl")
savePythonObject(normalized_total_markov_dict, output_markov_dict_folder +
                 output_markov_dict_prefix + "_" + IDF_prefix + "_" + phrase_mode_option + "_normalized.pkl")
end = time.time()
print("save Markov dictionaries took", end-start, "seconds")
# ---------------------------------------------------------------------------------------
