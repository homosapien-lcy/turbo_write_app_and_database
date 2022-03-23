from .preprocessing import *

# merge multiple tuples into one


def mergeTuples(tuple_arr):
    merged = ()
    for t in tuple_arr:
        merged += t

    return merged

# extract segment from sentence database
# id tupple is all the sentence id involved in this segment


def segmentLookUp(id_tupple, database_sentences, search_start_id):
    sentences_in_seg = []
    for id in id_tupple:
        relative_id = id - search_start_id
        sentences_in_seg.append(database_sentences[relative_id])

    # if string, merge into one string
    if type(sentences_in_seg[0]) is str:
        segment = '. '.join(sentences_in_seg) + '. '
    # if tuple, merge into tuple
    else:
        segment = mergeTuples(sentences_in_seg)

    return segment

# break each word into subwords
# if keep_two_ends set to True, with subword_len=3 the word: happy -> h ha hap app ppy py y
# else: happy -> hap app ppy
# not keeping two ends seems working better in "The implication of interpersonal neural synchronization"


def ngramSubwords(word, subword_len,
                  include_whole=True, keep_two_ends=False):
    pad_size = subword_len - 1
    # pad the word to keep two ends
    if keep_two_ends:
        padding = ' ' * pad_size
        padded_word = padding + word + padding
    else:
        # if not keeping two ends, no padding
        padded_word = word
        # when not keeping two ends, return the whole
        # word if smaller than subword_len, or
        # a empty set will be returned
        if len(word) < subword_len:
            return [word]

    subwords = []
    # for each sub word, add to list
    for i in range(0, len(padded_word) - pad_size):
        subwords.append(padded_word[i:i+subword_len].strip())

    # if also choose to include the whole original word
    if include_whole:
        subwords.append(word)

    return subwords

# leftEdgeSubwords create subwords from left edge
# min_subword_len is the minimum length of a subword
# for instance min_subword_len=3: quick -> qui quic quick


def leftEdgeSubwords(word, min_subword_len):
    subwords = []
    # for each sub word, add to list
    for i in range(min_subword_len, len(word)):
        subwords.append(word[:i])

    # also include the whole word which is missed by the above loop
    subwords.append(word)

    return subwords

# process each word in set with stemmer


def processWordSetWithStemmer(word_set, stemmer_option):
    if stemmer_option.lower() == "none":
        return word_set
    elif stemmer_option.lower() == "porter":
        return map(porter_stemmer.stem, word_set)
    elif stemmer_option.lower() == "snowball":
        return map(snowball_stemmer.stem, word_set)
    else:
        print("option not identified, go to default case and use no stemmer")
        return word_set

# break down sentence into unigrams


def unigramBreakDownWithStopwordsRemoval(s, stop_words, stemmer_option):
    word_set = set(s.split()) - stop_words
    stemmed_word_set = processWordSetWithStemmer(word_set, stemmer_option)
    return stemmed_word_set

# break down sentence into bigrams


def bigramBreakDown(s, stop_words, stemmer_option):
    bigram_arr = nltk.bigrams(s.split())
    bigram_arr = [' '.join(bi) for bi in bigram_arr]
    return set(bigram_arr)

# break down each word into subwords of length subword_len


def subwordBreakDown(s, stop_words, stemmer_option,
                     subwords_converter=ngramSubwords, subword_len=5):
    # first, segment into unigrams
    unigram_bag = unigramBreakDownWithStopwordsRemoval(
        s, stop_words, stemmer_option)

    subword_bag = []
    # break each word in bag into subwords
    for uni in unigram_bag:
        subword = subwords_converter(uni, subword_len)
        subword_bag.extend(subword)

    return set(subword_bag)

# calculate the query coverage score: total words covered / query length
# default with empty stop words
# break down operator turns segment into coverage units


def queryCoverageScore(query, I_, D_, segment,
                       stop_words, stemmer_option,
                       break_down_operator=subwordBreakDown):
    # check type of segment, if not string, concatenate
    if type(segment) is not str:
        text_segment = ' '.join(segment)

    # remove punctuation and numerics for coverage score
    punctless_segment = removeNonAlphaAndConnection(text_segment)
    punctless_segment = subPunct(punctless_segment, punct_list)

    # stopwords not count as coverage
    query_wordset = break_down_operator(query.lower(),
                                        stop_words, stemmer_option)
    segment_wordset = break_down_operator(punctless_segment.lower(),
                                          stop_words, stemmer_option)

    # intersection
    query_coverage = query_wordset & segment_wordset

    coverage_len = len(query_coverage)
    query_len = len(query_wordset)

    # edge case of empty query
    if query_len == 0:
        return 1

    return coverage_len / query_len

# just use -distance as similarity score


def distanceScore(query, I_, D_, segment,
                  stop_words, stemmer_option):
    return -D_


# generate I_D_segment_arr
# I_D_segment_arr has format: (I_, D_, segment)
# segment is the hit segment
# in default case, where there is only 1 batch, search_start_id=0


def to_I_D_segment_arr(I_arr, D_arr,
                       database_sentences, database_sentence_id,
                       search_start_id=0):
    I_D_segment_arr = []
    for i in range(0, len(I_arr)):
        I_ = I_arr[i]
        D_ = D_arr[i]
        segment = segmentLookUp(
            database_sentence_id[I_], database_sentences, search_start_id)
        I_D_segment = (I_, D_, segment)
        I_D_segment_arr.append(I_D_segment)

    return I_D_segment_arr


# display the sentence search results
# I_ and D_ is the ID and distance of found neighbor


def displayANeighbor(I_D_segment):
    # case of no coverage score
    if len(I_D_segment) == 3:
        I_, D_, segment = I_D_segment
        print("We found segment with id", I_, ":",
              segment, "is", D_, "away from the query")
    # case with coverage score
    elif len(I_D_segment) == 4:
        I_, D_, segment, coverage_score = I_D_segment
        print("We found segment with id", I_, ":",
              segment, "is", D_, "away from the query with distance score", coverage_score)
    # incorrect formatting if neither
    else:
        print("Incorrect formatting, expect 3 or 4 elements in the segment.")

# display search results


def displaySearchResults(I_D_segment_arr):
    for i in range(0, len(I_D_segment_arr)):
        print("The", str(i), "match is:")
        displayANeighbor(I_D_segment_arr[i])

# add score to the I_D_segment_arr


def addScore(query, I_D_segment_arr, stop_words, stemmer_option, scoring_fun):
    I_D_segment_coverage_arr = []
    for I_, D_, segment in I_D_segment_arr:
        coverage_score = scoring_fun(query, I_, D_, segment,
                                     stop_words, stemmer_option)
        I_D_segment_coverage = (I_, D_, segment, coverage_score)
        I_D_segment_coverage_arr.append(I_D_segment_coverage)

    return I_D_segment_coverage_arr

# rerank search result in I_D_segment_arr


def rerankSearchByScoringFunction(query, I_D_segment_arr,
                                  stop_words=set([]),
                                  stemmer_option="None",
                                  scoring_fun=queryCoverageScore):
    I_D_segment_coverage_arr = addScore(
        query, I_D_segment_arr, stop_words, stemmer_option, scoring_fun)
    # sort by the 4th value (score)
    sorted_I_D_segment_coverage_arr = sorted(
        I_D_segment_coverage_arr, key=lambda x: x[3], reverse=True)

    return sorted_I_D_segment_coverage_arr


'''
def test_rerankSearchByScoringFunction():
    query = "I have interpersonal burgers and beers and hotdogs"
    I_D_segment_arr = [
        (1, 0.1, "I have interpersonal burgers and beers and hotdogs"),
        (2, 0.2, "I have interpersonal burgers beers hotdogs"),
        (3, 0.2, "I have interpersonal. burgers beers hotdogs"),
        (4, 0.3, "a b n"),
        (5, 0.3, "a b n, a b n"),
        (6, 0.4, "I have beers hotdogs."),
        (7, 0.4, "I have beers hotdogs, I have beers hotdogs.")
    ]
    print(I_D_segment_arr)
    reranked_I_D_segment_arr = rerankSearchByScoringFunction(
        query, I_D_segment_arr, scoring_fun=queryCoverageScore)
    print("without stopwords", reranked_I_D_segment_arr)
    reranked_I_D_segment_arr = rerankSearchByScoringFunction(
        query, I_D_segment_arr, scoring_fun=queryCoverageScore, stop_words=stop_words_whole)
    print("without all stopwords", reranked_I_D_segment_arr)


test_rerankSearchByScoringFunction()
'''

'''
def test_subwordBreakDown():
    print('happy:', subwordBreakDown('happy', stop_words=set([]), subword_len=2))
    print('happpy:', subwordBreakDown(
        'happpy', stop_words=set([]), subword_len=2))
    print('happppy:', subwordBreakDown(
        'happppy', stop_words=set([]), subword_len=2))

    print('happppy life:', subwordBreakDown(
        'happppy life', stop_words=set([]), subword_len=2))
    print('happppy life ttuj:', subwordBreakDown(
        'happppy life ttuj', stop_words=set([]), subword_len=2))
    print('happppy and life and ttuj:', subwordBreakDown('happppy and life and ttuj',
                                                         stop_words=set([]), subword_len=2))
    print('happppy and life and ttuj:', subwordBreakDown('happppy and life and ttuj',
                                                         stop_words=stop_words_whole, subword_len=2))


test_subwordBreakDown()
'''
