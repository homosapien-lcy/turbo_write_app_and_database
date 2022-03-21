import time

from sklearn.cluster import MiniBatchKMeans
from python_utils.sentenceEmbeddingUtils import *

collection_folder = sys.argv[1]
idf_info_fn = sys.argv[2]
subject = sys.argv[3]
output_folder = sys.argv[4]
trained_model_file = sys.argv[5]

if collection_folder[-1] != '/':
    collection_folder += '/'

if output_folder[-1] != '/':
    output_folder += '/'

checkAndCreateFolder(output_folder)

fast_text_path = "fasttext"
fasttext_model_folder = fasttext_folder + \
    "result/fasttext_model_dim_150_min_df_100/"
bin_file_tail = "_fasttext_model.bin"
vec_file_tail = "_fasttext_model.vec"

embedding_processing_batch_size = 5000000
clustering_processing_batch_size = 10000

model_bin = fasttext_model_folder + subject + bin_file_tail
model_vec = fasttext_model_folder + subject + vec_file_tail

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
else:
    # load the idf model file
    idf_info = loadPythonObject(idf_info_fn)
    print("finish loading idf info")
    # initialize embedding
    sentence_database_embedding = SentenceEmbedding(idf_info)
    print("embedding has been initilized")
    # set the option for using idf weighting
    IDF_weighting_option = True

default_IDF_weight_option = 0
spell_correct_option = False

VP_collection_fn_arr = getFilenamesFromFolder(collection_folder)

# load the kmeans model
print("loading pre-trained model")
mini_batch_kmeans = loadPythonObject(trained_model_file)
n_clusters = mini_batch_kmeans.n_clusters

# run and get the labels
# ----------------------------------------------------------------------
# open files for writing
phrase_cluster_file_dict = {i: open(
    output_folder + "cluster_" + str(i) + "_phrase", 'w') for i in range(0, n_clusters)}
embedding_cluster_file_dict = {i: open(
    output_folder + "cluster_" + str(i) + "_embedding", 'w') for i in range(0, n_clusters)}
for VP_collection_fn in VP_collection_fn_arr:
    start = time.time()
    cur_VP_collection = loadPythonObject(VP_collection_fn)
    cur_phrase_collection = [extractedPatternToPhrase(
        VP) for VP in cur_VP_collection]

    # label for all data in the pkl file
    cur_phrase_labels = []
    for batch_cur_phrase_collection in chunked(cur_phrase_collection, embedding_processing_batch_size):
        # embed words
        batch_cur_embedding_LUT = getEmbeddingLUTFromFastText(
            batch_cur_phrase_collection, fast_text_path, model_bin)
        batch_cur_segment_vec_arr = sentence_database_embedding.embedSentenceWithEmbeddingLUTArrMP(
            batch_cur_phrase_collection, batch_cur_embedding_LUT,
            weighted_by_IDF=IDF_weighting_option, default_IDF_weight=default_IDF_weight_option,
            spell_correct=spell_correct_option,
            mp_batch_size=100000)

        # label and data collected for the batch
        batch_cur_phrase_labels = []
        batch_cur_phrase_arr = []
        batch_cur_embedding_arr = []
        for i in range(0, len(batch_cur_segment_vec_arr) + clustering_processing_batch_size, clustering_processing_batch_size):
            clus_batch_start = i
            clus_batch_end = i + clustering_processing_batch_size
            # extract the clustering batch from the batch data with index
            clus_batch_phrase_arr = batch_cur_phrase_collection[clus_batch_start:clus_batch_end]
            clus_batch_embedding_arr = batch_cur_segment_vec_arr[clus_batch_start:clus_batch_end, :]

            # save data with labels
            # check for empty batch
            if len(clus_batch_phrase_arr) > 0:
                # predict
                clus_batch_labels = mini_batch_kmeans.predict(
                    clus_batch_embedding_arr)
                # collect labels of each clustering batch to processing batch
                batch_cur_phrase_labels.extend(list(clus_batch_labels))
                batch_cur_phrase_arr.extend(clus_batch_phrase_arr)
                batch_cur_embedding_arr.extend(
                    clus_batch_embedding_arr.tolist())

        # save results in each batch
        # construct VP label dictionary
        batch_saving_start = time.time()
        VP_label_dict = labelArrToIndexDict(batch_cur_phrase_labels)
        # save by dictionary
        extractClusterAndSave(batch_cur_phrase_arr,
                              VP_label_dict,
                              phrase_cluster_file_dict)
        extractClusterAndSave(batch_cur_embedding_arr,
                              VP_label_dict,
                              embedding_cluster_file_dict)

        # collect labels into all labels of the pkl file
        cur_phrase_labels.extend(batch_cur_phrase_labels)
        batch_saving_end = time.time()
        print("saving this batch took", batch_saving_end -
              batch_saving_start, "seconds")

    end = time.time()
    print("predicting", VP_collection_fn, "took", end - start, "seconds")

    start = time.time()
    # save results
    # save VP labels
    pure_file_name = VP_collection_fn.split('/')[1]
    VP_labels_file_prefix = pure_file_name.split('.')[0]
    VP_labels_filename = output_folder + \
        VP_labels_file_prefix + "_kmeans_clustering_labels.pkl"
    savePythonObject(cur_phrase_labels, VP_labels_filename)

    end = time.time()
    print("saving to files took", end - start, "seconds")

# ----------------------------------------------------------------------

# close all cluster files afterwards
for k in phrase_cluster_file_dict.keys():
    phrase_cluster_file_dict[k].close()

for k in embedding_cluster_file_dict.keys():
    embedding_cluster_file_dict[k].close()
