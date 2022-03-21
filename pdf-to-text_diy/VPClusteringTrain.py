import time

from sklearn.cluster import MiniBatchKMeans
from python_utils.sentenceEmbeddingUtils import *
from python_utils.markovDictUtils import *

from RDRPOSTagger import *
RDRPOSTagger = RDRPOSTagger()
RDRPOSTagger.englishSetup()


def runGenerateRDRTag(sentence):
    return generateRDRTags(RDRPOSTagger, sentence)


section_text_fn = sys.argv[1]
idf_info_fn = sys.argv[2]
subject = sys.argv[3]
# option for loading trained model file for fine tuning
trained_model_fn = sys.argv[4]
n_clusters = int(sys.argv[5])
phrase_mode_option = sys.argv[6]
kmeans_model_prefix = sys.argv[7]

fast_text_path = "fasttext"
fasttext_model_folder = fasttext_folder + \
    "result/fasttext_model_dim_150_min_df_100/"
bin_file_tail = "_fasttext_model.bin"
vec_file_tail = "_fasttext_model.vec"

reading_batch_size = 10000
clustering_processing_batch_size = 10000
paragraph_length_cut = 20
sentence_length_cut = 5

model_bin = fasttext_model_folder + subject + bin_file_tail
model_vec = fasttext_model_folder + subject + vec_file_tail

# if not provided, initialize a new one
if trained_model_fn.lower() == "none":
    print("starting new model")
    mini_batch_kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        random_state=0,
        batch_size=clustering_processing_batch_size,
        reassignment_ratio=5e-2)
else:
    print("loading pre-trained model")
    mini_batch_kmeans = loadPythonObject(trained_model_file)
    # overwrite n_clusters parameter
    n_clusters = mini_batch_kmeans.n_clusters

# get embedding by fasttext_model[word], which also handles oov
# gensim similarity cannot handle oov...
# fasttext_model = fasttext.load_model(model_bin)
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

section_text_file = open(section_text_fn, 'r')
for batch_index, paragraph_batch in enumerate(chunked(section_text_file, reading_batch_size)):
    print("processing batch", batch_index)
    # if paragraph < paragraph_length_cut (invalid paragraph), remove
    # ---------------------------------------------------------------------------------------
    start = time.time()
    paragraph_batch = filterStringsTooShort(
        paragraph_batch, paragraph_length_cut)
    end = time.time()
    print("filter string for this batch took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # extract phrases
    # ---------------------------------------------------------------------------------------
    start = time.time()
    phrase_batch = paragraphToPatternPhraseArrSP(paragraph_batch, sentence_length_cut,
                                                 relation_VP_pattern, runGenerateRDRTag,
                                                 extractPatternOperator=extractPatternAndJoinNeighbor,
                                                 phrase_mode=phrase_mode_option)
    phrase_batch = list(flatten(phrase_batch))
    end = time.time()
    print("paragraph to phrase took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # generate fasttext LUT
    # ---------------------------------------------------------------------------------------
    start = time.time()
    batch_cur_embedding_LUT = getEmbeddingLUTFromFastText(
        phrase_batch, fast_text_path, model_bin)
    end = time.time()
    print("getting word embedding from fasttext took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # generate embeddings
    # ---------------------------------------------------------------------------------------
    start = time.time()
    batch_phrase_embedding = sentence_database_embedding.embedSentenceWithEmbeddingLUTArrSP(
        phrase_batch, batch_cur_embedding_LUT,
        weighted_by_IDF=IDF_weighting_option, default_IDF_weight=default_IDF_weight_option,
        spell_correct=spell_correct_option)
    end = time.time()
    print("embedding took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # generate embeddings
    # ---------------------------------------------------------------------------------------
    start = time.time()
    # use to fit minibatch kmeans
    mini_batch_kmeans.partial_fit(batch_phrase_embedding)
    end = time.time()
    print("training took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

# save the kmeans model
print("finish training, saving the model")
kmeans_model_file_name = kmeans_model_prefix + "_" + \
    IDF_prefix + "_" + phrase_mode_option + "_kmeans_model.pkl"
savePythonObject(mini_batch_kmeans, kmeans_model_file_name)
