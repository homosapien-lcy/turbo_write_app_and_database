import sys
import time
import numpy as np
import faiss

from python_utils.databaseUtils import *
from python_utils.sentenceEmbeddingUtils import *

dimension = 150
num_of_top_per_batch = 1000

total_start_id = 0
total_end_id = 23000000
processing_batch_size = 1000000
embedding_db_folder = "pubmed_title_abstract_sentence_embedding/"

db_sentence_file_tail = "_sentence_db.pkl"
db_embedding_file_tail = "_sentence_embedding_mat.npy"
db_embedding_id_tail = "_sentence_embedding_mat_id.pkl"

subject_prefix = "pubmed_title_abstract"
range_prefix_dict = {}
for i in range(total_start_id, total_end_id, processing_batch_size):
    key = str(i) + '_' + str(i+processing_batch_size-1)
    val_file_prefix = subject_prefix + '_' + key
    val_start_id = i
    range_prefix_dict[key] = [val_file_prefix, val_start_id]

# initialize index
# ---------------------------------------------------------------------------------
index_type = sys.argv[1]

if index_type == 'flat':
    faiss_index = faiss.IndexFlatL2(dimension)
elif index_type == 'HNSW':
    # much faster than flat, but consume much more memory
    HNSW_neighbors = 32
    faiss_index = faiss.IndexHNSWFlat(dimension, HNSW_neighbors)
elif index_type == 'IVF':
    # speed between HNSW and flat, also memory efficient, but not as accurate
    # number of cells
    nlist = 100
    quantizer = faiss.IndexFlatL2(dimension)
    faiss_index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
    # IVF needs training
    faiss_index.train(database_vec)
    # number of cells visited during search
    faiss_index.nprobe = 10
else:
    print("Only support db type of flat, HNSW and IVF")
    sys.exit(0)
# ---------------------------------------------------------------------------------

# process query
# ---------------------------------------------------------------------------------
subject = sys.argv[2]
idf_info_fn = sys.argv[3]

# load sentence embedding class
fast_text_path = "fasttext"
fasttext_model_folder = fasttext_folder + \
    "result/fasttext_model_dim_150_min_df_100/"
bin_file_tail = "_fasttext_model.bin"
vec_file_tail = "_fasttext_model.vec"

model_bin = fasttext_model_folder + subject + bin_file_tail
model_vec = fasttext_model_folder + subject + vec_file_tail

fasttext_model = fasttext.load_model(model_bin)
idf_info = loadPythonObject(idf_info_fn)
sentence_database_embedding = SentenceEmbedding(
    idf_info=idf_info, word_embed_model=fasttext_model)

# process query
#query = "autosomal dominant optic atrophy adoa omim 15 is the most common form of hereditary optic neuropathy with an estimated prevalence between 19 19 19 and 20 20 20 in different populations 21 21 it is characterized by insidious onset with a selective degeneration of retinal ganglion cells variable loss of visual acuity temporal optic nerve pallor tritanopia and development of central paracentral or cecocentral scotomas 99 99 adoa is inherited in an autosomal dominant manner with high interfamilial and intrafamilial phenotypic variability and incomplete penetrance. mutations in the optic atrophy 99 opa1 gene that consists of 0 coding exons are responsible for approximately 5 of cases. opa1 encodes a large guanosine triphosphatase gtpase implicated in the formation and maintenance of the mitochondrial network 6 and in protection against apoptosis by segregating cytochrome inside the mitochondrial cristae 100 100 opa1 comprises a highly basic terminus a dynamin gtpase domain and a terminus."
#query = "prosocial behavior is beneficial to our society"
#query = "interpersonal neural synchrony in dorsolateral prefrontal cortex"
#query = "The prosocial effect of interpersonal behavior synchronization"
query = "The interpersonal behavior synchronization can promote prosocial behavior"
#query = "The implication of interpersonal neural synchronization"
#query = "The neural mechanisms of empathy"
#query = "mRNA across cell membrane"
#query = "Teachers cannot achieve their goals without the cooperation of students."
processed_query = processSimilaritySearchQuery(query)
query_vec = sentence_database_embedding.embedSentence(processed_query)
# faiss search only takes a numpy matrix
wrapped_query_vec = np.array([query_vec]).astype('float32')
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# sort range by the first number
list_of_ranges = sorted(list(range_prefix_dict.keys()),
                        key=lambda x: int(x.split('_')[0]))
print('list_of_ranges:', list_of_ranges)
# how many databases to load for each search
num_each_search_batch = 8
all_I_D_segment_arr = []
for search_range_batch in chunked(list_of_ranges, num_each_search_batch):
    batch_database_sentences = []
    batch_database_vec = []
    batch_database_sentence_id = []
    batch_search_start_id = float('Inf')
    # go through each search range and load data
    for search_range in search_range_batch:
        range_prefix_for_search = range_prefix_dict[search_range][0]
        search_start_id = range_prefix_dict[search_range][1]

        batch_search_start_id = min(batch_search_start_id, search_start_id)

        # determine file name
        database_sentences_fn = embedding_db_folder + \
            range_prefix_for_search + db_sentence_file_tail
        database_vec_fn = embedding_db_folder + \
            range_prefix_for_search + db_embedding_file_tail
        database_sentence_id_fn = embedding_db_folder + \
            range_prefix_for_search + db_embedding_id_tail

        start = time.time()

        # load data
        database_sentences = loadPythonObject(database_sentences_fn)
        # faiss must use float32
        database_vec = np.load(database_vec_fn).astype('float32')
        database_sentence_id = loadPythonObject(database_sentence_id_fn)

        batch_database_sentences.extend(database_sentences)
        batch_database_vec.append(database_vec)
        batch_database_sentence_id.extend(database_sentence_id)

        end = time.time()
        print("Loading", database_sentences_fn,
              "takes", end - start, "seconds")

    # concatenate db
    batch_database_vec = np.concatenate(batch_database_vec, axis=0)

    print("number of sentences", len(batch_database_sentences))
    print("shape of similarity matrix", batch_database_vec.shape)
    print("number of similarity matrix id", len(batch_database_sentence_id))

    # constructing DB for search
    faiss_index.add(batch_database_vec)
    print("number of members:", faiss_index.ntotal)

    # search
    start = time.time()
    num_of_top_weighted_by_batch = int(
        (len(search_range_batch) * num_of_top_per_batch) / num_each_search_batch)
    D, I = faiss_index.search(wrapped_query_vec, num_of_top_weighted_by_batch)
    # search_start_id is used to map id to its corresponding batch id
    I_D_segment_arr = to_I_D_segment_arr(I[0], D[0],
                                         batch_database_sentences, batch_database_sentence_id,
                                         batch_search_start_id)
    all_I_D_segment_arr.extend(I_D_segment_arr)
    end = time.time()
    print("search for top", num_of_top_weighted_by_batch,
          "took", end - start, "seconds")

    # reset database for next round of search
    faiss_index.reset()

# ----------------------------------------------------------------------------------

# rerank search results
# ----------------------------------------------------------------------------------
rerank_option = sys.argv[4]

# rerank by distance
if rerank_option == "distance":
    reranked_I_D_segment_arr = rerankSearchByScoringFunction(
        query, I_D_segment_arr,
        stop_words=stop_words_whole,
        scoring_fun=distanceScore)
elif rerank_option == "coverage":
    reranked_I_D_segment_arr = rerankSearchByScoringFunction(
        query, I_D_segment_arr,
        stop_words=stop_words_whole, stemmer_option="Snowball",
        scoring_fun=queryCoverageScore)
else:
    print("invalid rerank option, rerank option must be distance and coverage")
    exit(0)

print("Query:", query)
displaySearchResults(reranked_I_D_segment_arr[0:10])
# ----------------------------------------------------------------------------------
