from python_utils.evidenceSearchUtils import *

dimension = 150
num_of_top_per_batch = 1000
num_results_return = 100

total_start_id = 0
total_end_id = 23000000
# use batch for memory saving
processing_batch_size = 1000000

embedding_db_folder = sys.argv[1]

tail_dict = {
    "sentence_file": "_sentence_db.pkl",
    "embedding_file": "_sentence_embedding_mat.npy",
    "embedding_id": "_sentence_embedding_mat_id.pkl"
}

subject_prefix = "pubmed_title_abstract"
range_prefix_dict = {}
for i in range(total_start_id, total_end_id, processing_batch_size):
    key = str(i) + '_' + str(i+processing_batch_size-1)
    val_file_prefix = subject_prefix + '_' + key
    val_start_id = i
    range_prefix_dict[key] = [val_file_prefix, val_start_id]

# constructing DB for search
# ---------------------------------------------------------------------------------------------------

# initialize index
# ---------------------------------------------------------------------------------------------------
index_type = sys.argv[2]

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
# ---------------------------------------------------------------------------------------------------

# initialize embedding
# ---------------------------------------------------------------------------------------------------
subject = sys.argv[3]
idf_info_fn = sys.argv[4]
rerank_option = sys.argv[5]

# load sentence embedding class
fast_text_folder = sys.argv[6]
fast_text_path = fast_text_folder + "fasttext"
fasttext_model_folder = fast_text_folder + \
    "result/fasttext_model_dim_150_min_df_100/"

bin_file_tail = "_fasttext_model.bin"
vec_file_tail = "_fasttext_model.vec"

model_bin = fasttext_model_folder + subject + bin_file_tail
model_vec = fasttext_model_folder + subject + vec_file_tail

fasttext_model = fasttext.load_model(model_bin)
idf_info = loadPythonObject(idf_info_fn)
sentence_database_embedding = SentenceEmbedding(
    idf_info=idf_info, word_embed_model=fasttext_model)

# ---------------------------------------------------------------------------------------------------


# start server
# ---------------------------------------------------------------------------------------------------
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request

app = Flask(__name__)


@app.route('/nexus', methods=['POST'])
def create_task():
    if not request.json:
        abort(400)

    query = request.json.get('query', "")

    print("get query for:")
    print(query)

    # search for evidences
    evidence = evidenceSearch(query,
                              faiss_index,
                              num_of_top_per_batch,
                              range_prefix_dict,
                              embedding_db_folder, tail_dict,
                              sentence_database_embedding,
                              spell_correct=False)

    # rerank
    reranked_evidence = evidenceRerank(query, evidence, rerank_option)

    # only send back text evidences themselves
    evidence_to_return = reranked_evidence[:num_results_return]
    # convert to dictionary
    evidence_to_return = [{
        'ID': str(e[0]),
        'title': removeExtraSpace(e[2][0]),
        'abstract': removeExtraSpace(e[2][1])
    } for e in evidence_to_return]

    reply = {
        'hits': evidence_to_return
    }

    return jsonify(reply), 201

# error catching


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    # set debug to False when serving, or the program will be started twice due to reloader!
    app.run(debug=True, port=4000)

# ---------------------------------------------------------------------------------------------------
