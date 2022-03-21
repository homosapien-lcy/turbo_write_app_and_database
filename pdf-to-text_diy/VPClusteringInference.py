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
trained_model_file = sys.argv[4]
phrase_mode_option = sys.argv[5]
output_folder = sys.argv[6]

if output_folder[-1] != '/':
    output_folder += '/'

checkAndCreateFolder(output_folder)

fast_text_path = "fasttext"
fasttext_model_folder = fasttext_folder + \
    "result/fasttext_model_dim_150_min_df_100/"
bin_file_tail = "_fasttext_model.bin"
vec_file_tail = "_fasttext_model.vec"

reading_batch_size = 10000
paragraph_length_cut = 20
sentence_length_cut = 5

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
print("loading pre-trained model")
mini_batch_kmeans = loadPythonObject(trained_model_file)
n_clusters = mini_batch_kmeans.n_clusters

# run and get the labels
# ---------------------------------------------------------------------------------------
# open files for writing
phrase_cluster_file_dict = {i: open(
    output_folder + "cluster_" + str(i) + "_phrase", 'w') for i in range(0, n_clusters)}
embedding_cluster_file_dict = {i: open(
    output_folder + "cluster_" + str(i) + "_embedding", 'w') for i in range(0, n_clusters)}

section_text_file = open(section_text_fn, 'r')
all_labels = []
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
    # flatten generates a generator object, which can only use once and
    # will return an empty array in second use!!!!! Thus need to wrap with list
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

    # generate labels
    # ---------------------------------------------------------------------------------------
    start = time.time()
    # use to fit minibatch kmeans
    # check for empty batch
    batch_labels = mini_batch_kmeans.predict(batch_phrase_embedding)
    batch_labels = list(batch_labels)
    all_labels.extend(batch_labels)

    end = time.time()
    print("predict took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

    # save embedding and phrases by label
    # ---------------------------------------------------------------------------------------
    start = time.time()
    VP_label_dict = labelArrToIndexDict(batch_labels)
    # save by dictionary
    extractClusterAndSave(phrase_batch,
                          VP_label_dict,
                          phrase_cluster_file_dict)
    extractClusterAndSave(batch_phrase_embedding.tolist(),
                          VP_label_dict,
                          embedding_cluster_file_dict)
    end = time.time()
    print("save phrases and embedding took", end-start, "seconds")
    # ---------------------------------------------------------------------------------------

start = time.time()
# save VP labels
VP_labels_filename = output_folder + IDF_prefix + "_" + \
    phrase_mode_option + "_kmeans_clustering_labels.pkl"
savePythonObject(all_labels, VP_labels_filename)

end = time.time()
print("saving all labels took", end - start, "seconds")

# ---------------------------------------------------------------------------------------
# close all cluster files afterwards
for k in phrase_cluster_file_dict.keys():
    phrase_cluster_file_dict[k].close()

for k in embedding_cluster_file_dict.keys():
    embedding_cluster_file_dict[k].close()
