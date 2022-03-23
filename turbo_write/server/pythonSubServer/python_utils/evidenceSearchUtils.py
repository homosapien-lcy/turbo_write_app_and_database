import sys
import time
import numpy as np
import faiss

from python_utils.databaseUtils import *
from python_utils.sentenceEmbeddingUtils import *

# function for query embedding


def generateWrappedQueryVec(query, embedding_obj,
                            do_normalize_word, do_normalize_sentence,
                            weighted_by_IDF,
                            default_IDF_weight,
                            spell_correct):
    # embed query
    processed_query = processSimilaritySearchQuery(query)
    query_vec = embedding_obj.embedSentence(processed_query,
                                            do_normalize_word, do_normalize_sentence,
                                            weighted_by_IDF,
                                            default_IDF_weight,
                                            spell_correct)
    # faiss search only takes a numpy matrix
    wrapped_query_vec = np.array([query_vec]).astype('float32')

    return wrapped_query_vec

# function for search with query


def evidenceSearch(query,
                   faiss_index,
                   num_of_top_per_batch,
                   range_prefix_dict,
                   embedding_db_folder, tail_dict,
                   embedding_obj,
                   # options for embedding
                   do_normalize_word=True, do_normalize_sentence=True,
                   weighted_by_IDF=True,
                   default_IDF_weight=None,
                   spell_correct=True):

    # embed query
    wrapped_query_vec = generateWrappedQueryVec(query, embedding_obj,
                                                do_normalize_word, do_normalize_sentence,
                                                weighted_by_IDF,
                                                default_IDF_weight,
                                                spell_correct)

    # search
    # sort range by the first number
    list_of_ranges = sorted(list(range_prefix_dict.keys()),
                            key=lambda x: int(x.split('_')[0]))

    # how many databases to load for each search
    num_each_search_batch = 4
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
                range_prefix_for_search + tail_dict["sentence_file"]
            database_vec_fn = embedding_db_folder + \
                range_prefix_for_search + tail_dict["embedding_file"]
            database_sentence_id_fn = embedding_db_folder + \
                range_prefix_for_search + tail_dict["embedding_id"]

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
                  "took", end - start, "seconds")

        # concatenate db
        batch_database_vec = np.concatenate(batch_database_vec, axis=0)

        print("number of sentences", len(batch_database_sentences))
        print("shape of similarity matrix", batch_database_vec.shape)
        print("number of similarity matrix id",
              len(batch_database_sentence_id))

        # constructing DB for search
        faiss_index.add(batch_database_vec)
        print("number of members:", faiss_index.ntotal)

        # search
        start = time.time()
        num_of_top_weighted_by_batch = int(
            (len(search_range_batch) * num_of_top_per_batch) / num_each_search_batch)
        D, I = faiss_index.search(
            wrapped_query_vec, num_of_top_weighted_by_batch)
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

    return all_I_D_segment_arr

# function for rerank


def evidenceRerank(query, I_D_segment_arr, rerank_option):
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

    return reranked_I_D_segment_arr

# function that returns loaded databases


def loadEmbeddingSearchDatabase(range_prefix_dict, embedding_db_folder, tail_dict):
    print("start loading embedding search database")
    start = time.time()
    list_of_ranges = sorted(list(range_prefix_dict.keys()),
                            key=lambda x: int(x.split('_')[0]))

    database_sentences = []
    database_matrix = []
    database_sentence_id = []
    for search_range in list_of_ranges:
        cur_start = time.time()
        range_prefix_for_search = range_prefix_dict[search_range][0]

        # determine file name
        cur_database_sentences_fn = embedding_db_folder + \
            range_prefix_for_search + tail_dict["sentence_file"]
        cur_database_matrix_fn = embedding_db_folder + \
            range_prefix_for_search + tail_dict["embedding_file"]
        cur_database_sentence_id_fn = embedding_db_folder + \
            range_prefix_for_search + tail_dict["embedding_id"]

        # load data
        cur_database_sentences = loadPythonObject(cur_database_sentences_fn)
        # faiss must use float32
        cur_database_matrix = np.load(cur_database_matrix_fn).astype('float32')
        cur_database_sentence_id = loadPythonObject(
            cur_database_sentence_id_fn)

        database_sentences.extend(cur_database_sentences)
        database_matrix.append(cur_database_matrix)
        database_sentence_id.extend(cur_database_sentence_id)

        cur_end = time.time()
        print("Loading", cur_database_sentences_fn,
              "took", cur_end - cur_start, "seconds")

    end = time.time()
    print("Loading took", end - start, "seconds")

    # concatenate db
    database_matrix = np.concatenate(database_matrix, axis=0)

    print("number of sentences", len(database_sentences))
    print("shape of similarity matrix", database_matrix.shape)
    print("number of similarity matrix id",
          len(database_sentence_id))

    return {
        "sentences": database_sentences,
        "matrix": database_matrix,
        "matrix_id": database_sentence_id
    }

# search with a preloaded faiss index


def evidenceSearchWithFaissIndex(query,
                                 faiss_index, num_of_top,
                                 embedding_database_dict, search_start_id,
                                 embedding_obj,
                                 # options for embedding
                                 do_normalize_word=True, do_normalize_sentence=True,
                                 weighted_by_IDF=True,
                                 default_IDF_weight=None,
                                 spell_correct=True):
    start = time.time()
    # embed query
    wrapped_query_vec = generateWrappedQueryVec(query, embedding_obj,
                                                do_normalize_word, do_normalize_sentence,
                                                weighted_by_IDF,
                                                default_IDF_weight,
                                                spell_correct)

    # search
    D, I = faiss_index.search(wrapped_query_vec, num_of_top)

    # search_start_id is used to map id to its corresponding batch id
    I_D_segment_arr = to_I_D_segment_arr(I[0], D[0],
                                         embedding_database_dict["sentences"],
                                         embedding_database_dict["matrix_id"],
                                         search_start_id)

    end = time.time()
    print("search for top", num_of_top,
          "took", end - start, "seconds")

    return I_D_segment_arr
