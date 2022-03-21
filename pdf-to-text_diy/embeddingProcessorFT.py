import sys
import time

from python_utils.sentenceEmbeddingUtils import *

subject = sys.argv[1]
idf_info_fn = sys.argv[2]
sentence_DB_fn = sys.argv[3]
# how many sentence form a segment for search
num_group = int(sys.argv[4])
output_prefix = sys.argv[5]
save_folder = sys.argv[6]

if save_folder[-1] != '/':
    save_folder += '/'

checkAndCreateFolder(save_folder)

fast_text_path = "fasttext"
fasttext_model_folder = fasttext_folder + \
    "result/fasttext_model_dim_150_min_df_100/"
bin_file_tail = "_fasttext_model.bin"
vec_file_tail = "_fasttext_model.vec"

processing_batch_size = 1000000

model_bin = fasttext_model_folder + subject + bin_file_tail
model_vec = fasttext_model_folder + subject + vec_file_tail

# get embedding by fasttext_model[word], which also handles oov
# gensim similarity cannot handle oov...
# fasttext_model = fasttext.load_model(model_bin)
idf_info = loadPythonObject(idf_info_fn)
print("finish loading idf info")

sentence_database_embedding = SentenceEmbedding(idf_info)
print("embedding has been initilized")

sentence_DB_file = open(sentence_DB_fn, 'r')
segment_batch = []
batch_id_start = 0
start = time.time()
# *[iter(sentence_DB_file)]*2 iterate through the file two lines at a time
for segment_index, (title, abstract) in enumerate(zip(*[iter(sentence_DB_file)]*2)):
    # accumulate data
    segment_batch.append((title.strip(), abstract.strip()))

    # if reach batch size, process, save and restart
    if (segment_index + 1) % processing_batch_size == 0:
        # preprocess texts
        # join title and abstract
        text_batch = [s[0] + '. ' + s[1] for s in segment_batch]
        # preprocessing
        text_batch = processNxmlContentArrMP(text_batch)
        # remove period for embedding step
        text_batch = [t.replace('.', '') for t in text_batch]

        processAndSaveSegmentBatch(text_batch, segment_batch,
                                   batch_id_start, segment_index,
                                   sentence_database_embedding,
                                   fast_text_path, model_bin, num_group,
                                   save_folder, output_prefix)

        # report and restart time
        end = time.time()
        print("embedding batch", (segment_index + 1) /
              processing_batch_size, "took", end - start, "seconds")
        start = time.time()

        # restart batch
        segment_batch = []
        batch_id_start += processing_batch_size

# process last batch is not empty
if len(segment_batch) > 0:
    # preprocess texts
    # join title and abstract
    text_batch = [s[0] + '. ' + s[1] for s in segment_batch]
    # preprocessing
    text_batch = processNxmlContentArrMP(text_batch)
    # remove period for embedding step
    text_batch = [t.replace('.', '') for t in text_batch]

    processAndSaveSegmentBatch(text_batch, segment_batch,
                               batch_id_start, segment_index,
                               sentence_database_embedding,
                               fast_text_path, model_bin, num_group,
                               save_folder, output_prefix)

    end = time.time()
    print("embedding batch", (segment_index + 1) /
          processing_batch_size, "took", end - start, "seconds")

# close file
sentence_DB_file.close()

# remove temp file
runRM(temp_word_batch_fn)
