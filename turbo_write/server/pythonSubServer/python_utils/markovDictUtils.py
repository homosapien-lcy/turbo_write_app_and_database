from functools import reduce
from python_utils.preprocessing import *

start_symbol = "<START>"
end_symbol = "<END>"

'''
generate arr of patterns from a paragraph
phrase_modes: 
fpo = first_phrase_only: only keep the first phrase in a sentence, for instance [[('house', 'NN)], [('horse', 'NN)]] -> [[('house', 'NN)]]
cp = concatenate phrase: join all phrases in a sentence into one phrase, for instance [[('house', 'NN)], [('horse', 'NN)]] -> [[('house', 'NN), ('horse', 'NN)]]
asp = as separate phrases: [('house', 'NN)], [('horse', 'NN)] will later be processed as separate neighbor phrases
'''


def paragraphToPattern(paragraph, sentence_length_cut,
                       target_pattern, tag_operator,
                       extractPatternOperator,
                       phrase_mode):
    # divide into sentences
    sentences = paragraph.split('.')
    # remove spaces on two ends
    sentences = [s.strip() for s in sentences]
    # filter length
    sentences = filterStringsTooShort(sentences, sentence_length_cut)
    # extract pattern for each sentence
    patterns = [extractPatternOperator(s, target_pattern, tag_operator)
                for s in sentences]
    # if show only first phrase only, only keep the first phrase
    # in a sentence
    phrase_mode = phrase_mode.lower()
    if phrase_mode == 'fpo':
        # p[:1] same as p[1], except it will return empty in case of empty array
        # instead of giving exception like p[1]
        patterns = [p[:1] for p in patterns]
    elif phrase_mode == 'cp':
        patterns = [[flatten(p)] for p in patterns]
    elif phrase_mode == 'asp':
        pass
    else:
        print("invalid phrase mode, should be fpo, cp or asp, use the default option asp")
        pass

    patterns = flatten(patterns)
    patterns = [extractedPatternToPhrase(p) for p in patterns]
    # filter empty strings
    patterns = filterStringsTooShort(patterns, 0)

    return patterns

# extract pattern for single processor


def paragraphToPatternPhraseArrSP(paragraph_arr, sentence_length_cut,
                                  target_pattern, tag_operator,
                                  extractPatternOperator=extractPatternAndJoinNeighbor,
                                  phrase_mode='asp'):
    patterns_arr = map(lambda p: paragraphToPattern(p, sentence_length_cut,
                                                    target_pattern, tag_operator,
                                                    extractPatternOperator,
                                                    phrase_mode), paragraph_arr)
    return patterns_arr

# extract pattern for multi processor


def paragraphToPatternPhraseArrMP(paragraph_arr, sentence_length_cut,
                                  target_pattern, tag_operator,
                                  extractPatternOperator=extractPatternAndJoinNeighbor,
                                  phrase_mode='asp'):
    with eval(core_pool_4) as pool:
        patterns_arr = pool.map(partial(paragraphToPattern,
                                        sentence_length_cut=sentence_length_cut,
                                        target_pattern=target_pattern,
                                        tag_operator=tag_operator,
                                        extractPatternOperator=extractPatternOperator,
                                        phrase_mode=phrase_mode),
                                paragraph_arr, 1000)
        pool.close()
        pool.join()

        return patterns_arr

# convert pattern phrase to markov dictionary

# helper function for addToMarkovDictOrAddOne


def addToCountDictOrAddOne(count_dict, cur_state):
    if cur_state in count_dict.keys():
        count_dict[cur_state] += 1
    else:
        count_dict[cur_state] = 1

# helper function for phraseSequenceToMarkovDictionary


def addToMarkovDictOrAddOne(markov_dict, prev_state, cur_state):
    # if not in markov dict, initialize an empty counter
    if prev_state not in markov_dict.keys():
        markov_dict[prev_state] = Counter([])

    # take out count dict
    count_dict = markov_dict[prev_state]
    # update count dict
    addToCountDictOrAddOne(count_dict, cur_state)

# helper function that converts sequence to markov dictionary


def sequenceToMarkovDictionary(phrase_cluster_sequence):
    markov_dict = {}
    previous_cluster = start_symbol
    for i in range(0, len(phrase_cluster_sequence)):
        pcs_i = phrase_cluster_sequence[i]
        # use string to uniform type
        current_cluster = str(pcs_i)
        # update dictionary
        addToMarkovDictOrAddOne(markov_dict, previous_cluster, current_cluster)
        # update previous cluster
        previous_cluster = current_cluster

    # current_cluster after the loop will record the cluster of last phrase
    addToMarkovDictOrAddOne(markov_dict, current_cluster, end_symbol)

    return markov_dict


def phraseSequenceToMarkovDictionary(phrase_sequence, embedding_operator, kmeans_model):
    # generate embeddings
    phrase_embedding_sequence = embedding_operator(phrase_sequence)
    # generate cluster of each phrase
    phrase_cluster_sequence = kmeans_model.predict(phrase_embedding_sequence)
    # generate markov dictionary that record the next cluster of a cluster
    # markov dictionary map from prev state to a counter of cur state
    markov_dict = sequenceToMarkovDictionary(phrase_cluster_sequence)

    return markov_dict

# single processor version for array


def phraseSequenceToMarkovDictionaryArrSP(phrase_sequence_arr, embedding_operator, kmeans_model):
    markov_dict_arr = map(lambda ps: phraseSequenceToMarkovDictionary(
        ps, embedding_operator, kmeans_model), phrase_sequence_arr)
    return markov_dict_arr

# multi processor version for array


def phraseSequenceToMarkovDictionaryArrMP(phrase_sequence_arr, embedding_operator, kmeans_model):
    with eval(core_pool_4) as pool:
        markov_dict_arr = pool.map(partial(phraseSequenceToMarkovDictionary,
                                           embedding_operator=embedding_operator,
                                           kmeans_model=kmeans_model),
                                   phrase_sequence_arr, 100)
        pool.close()
        pool.join()

        return markov_dict_arr

# function that merges two markov dictionary


def mergeTwoMarkovDict(markov_dict_1, markov_dict_2):
    # all keys in dict 1 and 2
    whole_key_set = markov_dict_1.keys() | markov_dict_2.keys()

    merged_dict = {}
    for k in whole_key_set:
        # cases of unique key
        if k not in markov_dict_1.keys():
            merged_dict[k] = markov_dict_2[k]
        elif k not in markov_dict_2.keys():
            merged_dict[k] = markov_dict_1[k]
        # case of common key
        else:
            merged_dict[k] = markov_dict_1[k] + markov_dict_2[k]

    return merged_dict

# function that merges an array of markov dictionary


def mergeMarkovDictArr(markov_dict_arr):
    return reduce(mergeTwoMarkovDict, markov_dict_arr)

# normalize a counter


def normalizeCounter(c):
    # sum counts
    total = sum(c.values())
    normalized_c = Counter([])
    for k in c.keys():
        normalized_c[k] = c[k] / total

    return normalized_c

# normalize markov dict


def normalizeMarkovDict(markov_dict):
    normalized_markov_dict = {}
    for k in markov_dict.keys():
        normalized_markov_dict[k] = normalizeCounter(markov_dict[k])

    return normalized_markov_dict

# sum the top_n in a counter


def counterTopSum(c, top_n):
    top_n_elements = c.most_common(top_n)
    top_n_values = [e[1] for e in top_n_elements]
    top_n_value_sum = sum(top_n_values)

    return top_n_value_sum


'''
def test_mergeMarkovDictArr():
    a = Counter([1, 2, 3, 1, 2])
    b = Counter([1, 2, 3, 1, 4])
    c = Counter([5, 5, 2])
    print(mergeMarkovDictArr([a, b, c]))


test_mergeMarkovDictArr()
'''
