import subprocess
import fasttext

from more_itertools import chunked
from functools import reduce
from spellchecker import SpellChecker

from .preprocessing import *
from .embeddingUtils import *
from .numericalAnalysisUtils import *

spell_checker = SpellChecker()
temp_word_batch_fn = "words_in_batch_to_embed_in_fasttext"
suppress_printing = True

# a class for analyzing the embedding sentences


class SentenceEmbedding:
    # allow embed using embedding LUT when word_embed_model is None
    def __init__(self, idf_info=None, word_embed_model=None):
        if idf_info is not None:
            self.num_docs = idf_info['num_docs']
            self.idf_vocab_dict = idf_info['idf_vocab_dict']
            self.idf_stopword_list = idf_info['idf_stopword_list']
            self.idf = idf_info['idf']

        self.word_embed_model = word_embed_model

    # return idf from a word
    def retrieveIDF(self, word):
        lookup_index = self.idf_vocab_dict[word]
        return self.idf[lookup_index]

    def embedWord(self, word, do_normalize):
        # fast text already returning a numpy array
        word_vec = self.word_embed_model[word]
        if do_normalize:
            word_vec = normalizeVector(word_vec)

        return word_vec

    def embedWordWithEmbeddingLUT(self, word, embeddingLUT, do_normalize):
        # if in dictionary
        if word in embeddingLUT.keys():
            # fast text already returning a numpy array
            word_vec = embeddingLUT[word]
        else:
            #print(word, "not found in embedding, use 0 vector instead")
            word_vec = embeddingLUT["NOT_FOUND"]

        if do_normalize:
            word_vec = normalizeVector(word_vec)

        return word_vec

    def IDFWeightLookup(self, word):
        # no weight for stopwords
        if word in self.idf_stopword_list:
            return 0
        elif word in self.idf_vocab_dict.keys():
            return self.retrieveIDF(word)

        # return None if not found in either stopwords or vocab dict
        return None

    # IDF look up with spelling and oov guard
    # put default weight here, allow flexible default weight
    def guardedIDFWeightLookup(self, word,
                               default_IDF_weight,
                               spell_correct):
        IDF_weight = self.IDFWeightLookup(word)
        # if not found
        if IDF_weight is None:
            # if spell check
            # spell check takes long time and sometimes unneccessary, thus
            # make it an option
            if spell_correct:
                # spell check
                # actually very slow...
                spell_checked_word = spell_checker.correction(word)
                if not suppress_printing:
                    print('word', word, 'is not found in IDF model, it may actually be a misspelled, looking up with the potential correct spelling',
                          spell_checked_word)

                # look up again
                IDF_weight = self.IDFWeightLookup(spell_checked_word)
                # if still not found, oov
                if IDF_weight is None:
                    if not suppress_printing:
                        print('still not found, return default IDF weight',
                              default_IDF_weight)
                    # use default weight
                    if default_IDF_weight is None:
                        # if not specified default idf weight is log(N/1) (ln(N/1))
                        # np.log is the default log use by sklearn idf
                        default_IDF_weight = np.log(self.num_docs / 1)

                    IDF_weight = default_IDF_weight
            # if choose not to spell check
            else:
                if not suppress_printing:
                    print('not found, choose not to spell check, return default IDF weight',
                          default_IDF_weight)
                IDF_weight = default_IDF_weight

        return IDF_weight

    # idf weighted embedding
    def IDFWeightedEmbedWord(self, word,
                             do_normalize_word, default_IDF_weight,
                             spell_correct):
        word_vec = self.embedWord(word, do_normalize_word)
        idf_weight = self.guardedIDFWeightLookup(
            word, default_IDF_weight, spell_correct)
        return idf_weight * word_vec

    # idf weighted embedding with LUT
    def IDFWeightedEmbedWordWithEmbeddingLUT(self, word, embeddingLUT,
                                             do_normalize_word, default_IDF_weight,
                                             spell_correct):
        word_vec = self.embedWordWithEmbeddingLUT(
            word, embeddingLUT, do_normalize_word)
        idf_weight = self.guardedIDFWeightLookup(
            word, default_IDF_weight, spell_correct)
        return idf_weight * word_vec

    def embedSentence(self, sentence,
                      do_normalize_word=True, do_normalize_sentence=True,
                      weighted_by_IDF=True,
                      default_IDF_weight=None,
                      spell_correct=True):

        BOW = sentence.lower().split()

        # for empty string, return zero array
        # since np.sum(np.array([]), axis=0) will return 0.0
        # thus cause dimension mismatch during numpy matrix conversion
        if len(BOW) == 0:
            return np.zeros(self.word_embed_model.get_dimension())

        weighted_word_vec_list = []
        # collect word vector
        for w in BOW:
            if weighted_by_IDF:
                weighted_word_vec = self.IDFWeightedEmbedWord(
                    w, do_normalize_word, default_IDF_weight, spell_correct)
            # if not weighted by IDF, return word vec with same weight
            else:
                weighted_word_vec = self.embedWord(w, do_normalize_word)

            weighted_word_vec_list.append(weighted_word_vec)

        # sum to get the TFIDF weighted sentence vec
        sentence_vec = np.sum(np.array(weighted_word_vec_list), axis=0)

        if do_normalize_sentence:
            sentence_vec = normalizeVector(sentence_vec)

        return sentence_vec

    def embedSentenceWithEmbeddingLUT(self, sentence, embeddingLUT,
                                      do_normalize_word=True, do_normalize_sentence=True,
                                      weighted_by_IDF=True,
                                      default_IDF_weight=None,
                                      spell_correct=True):
        BOW = sentence.lower().split()

        # for empty string, return zero array
        # since np.sum(np.array([]), axis=0) will return 0.0
        # thus cause dimension mismatch during numpy matrix conversion
        if len(BOW) == 0:
            return embeddingLUT["NOT_FOUND"]

        weighted_word_vec_list = []
        # collect word vector
        for w in BOW:
            if weighted_by_IDF:
                weighted_word_vec = self.IDFWeightedEmbedWordWithEmbeddingLUT(
                    w, embeddingLUT, do_normalize_word, default_IDF_weight, spell_correct)
            # if not weighted by IDF, return word vec with same weight
            else:
                weighted_word_vec = self.embedWordWithEmbeddingLUT(
                    w, embeddingLUT, do_normalize_word)

            weighted_word_vec_list.append(weighted_word_vec)

        # sum to get the TFIDF weighted sentence vec
        sentence_vec = np.sum(np.array(weighted_word_vec_list), axis=0)

        if do_normalize_sentence:
            sentence_vec = normalizeVector(sentence_vec)

        return sentence_vec

    # embed sentences with single core
    def embedSentenceArrSP(self, sentences,
                           do_normalize_word=True, do_normalize_sentence=True,
                           weighted_by_IDF=True,
                           default_IDF_weight=None,
                           spell_correct=True):

        # 10% faster than map and for loop
        sentence_vec_arr = [self.embedSentence(cur_sentence,
                                               do_normalize_word=do_normalize_word,
                                               do_normalize_sentence=do_normalize_sentence,
                                               weighted_by_IDF=weighted_by_IDF,
                                               default_IDF_weight=default_IDF_weight,
                                               spell_correct=spell_correct)
                            for cur_sentence in sentences]
        '''
        #sentence_vec_arr = []
        for i in range(0, len(sentences)):
            cur_sentence = sentences[i]
            cur_sentence_vec = self.embedSentence(cur_sentence,
                                                  do_normalize_word=do_normalize_word,
                                                  do_normalize_sentence=do_normalize_sentence,
                                                  weighted_by_IDF=weighted_by_IDF,
                                                  default_IDF_weight=default_IDF_weight,
                                                  spell_correct=spell_correct)

            sentence_vec_arr.append(cur_sentence_vec)
        '''

        return np.array(sentence_vec_arr)

    # multicore doesn't work! may due to the fact that all threads will try to use fasttext
    # which only has 1 resource
    '''
    # embed sentences with multicore
    def embedSentenceArrMP(self, sentences,
                           do_normalize_word=True, do_normalize_sentence=True,
                           weighted_by_IDF=True,
                           default_IDF_weight=None,
                           spell_correct=True):

        # use parallelism to speed up, use 1000 as chunk size
        with eval(pathos_core_pool_4) as pool:
            def runEmbed(s): return self.embedSentence(s,
                                                       do_normalize_word=do_normalize_word,
                                                       do_normalize_sentence=do_normalize_sentence,
                                                       weighted_by_IDF=weighted_by_IDF,
                                                       default_IDF_weight=default_IDF_weight,
                                                       spell_correct=spell_correct)
            sentence_vec_arr = pool.map(runEmbed, sentences)
            pool.close()
            pool.join()

        return np.array(sentence_vec_arr)
    '''

    # embed sentences with single core
    def embedSentenceWithEmbeddingLUTArrSP(self, sentences, embeddingLUT,
                                           do_normalize_word=True, do_normalize_sentence=True,
                                           weighted_by_IDF=True,
                                           default_IDF_weight=None,
                                           spell_correct=True):

        # 10% faster than map and for loop
        sentence_vec_arr = [self.embedSentenceWithEmbeddingLUT(cur_sentence, embeddingLUT,
                                                               do_normalize_word=do_normalize_word,
                                                               do_normalize_sentence=do_normalize_sentence,
                                                               weighted_by_IDF=weighted_by_IDF,
                                                               default_IDF_weight=default_IDF_weight,
                                                               spell_correct=spell_correct)
                            for cur_sentence in sentences]

        return np.array(sentence_vec_arr)

    # not faster than SP...
    # embed sentences with multicore
    def embedSentenceWithEmbeddingLUTArrMP(self, sentences, embeddingLUT,
                                           do_normalize_word=True, do_normalize_sentence=True,
                                           weighted_by_IDF=True,
                                           default_IDF_weight=None,
                                           spell_correct=True,
                                           mp_batch_size=10000):
        # use parallelism to speed up, use mp_batch_size as chunk size
        # SP: 63s per 100k sentences, MP: 41s per 100k sentences (chunk size 10k)
        with eval(core_pool_4) as pool:
            sentence_vec_arr = pool.map(partial(self.embedSentenceWithEmbeddingLUT, embeddingLUT=embeddingLUT,
                                                do_normalize_word=do_normalize_word,
                                                do_normalize_sentence=do_normalize_sentence,
                                                weighted_by_IDF=weighted_by_IDF,
                                                default_IDF_weight=default_IDF_weight,
                                                spell_correct=spell_correct), sentences, mp_batch_size)
            pool.close()
            pool.join()

        return np.array(sentence_vec_arr)


# convert a list of string to float


def strToFloat(str_of_float):
    return [float(x) for x in str_of_float]

# convert fasttext output to word_embedding LUT


def fastTextOutputToLUT(fast_text_output):
    embedding_str_arr = fast_text_output.strip().split('\n')
    vec_len = len(embedding_str_arr[0].split()) - 1
    # embedding LUT: word -> embedding vec
    embedding_LUT = {}
    for embedding_str in embedding_str_arr:
        embedding_str_l = embedding_str.split()
        word = embedding_str_l[0]
        embedding = np.array(strToFloat(embedding_str_l[1:]))
        embedding_LUT[word] = embedding

    embedding_LUT["NOT_FOUND"] = np.zeros(vec_len)

    return embedding_LUT

# helper function


def convertToWordSet(s):
    if type(s) != set:
        return set(s.split())
    else:
        return s

# helper function for set merging


def mergeOperator(x, y):
    # convert on the fly to save memory
    return convertToWordSet(x) | convertToWordSet(y)


# helper for toChunkWordSet


def segmentChunkToWordSet(chunk):
    word_arr = []
    for seg in chunk:
        # extend only takes k, faster than merge (|)
        word_arr.extend(seg.split())

    return set(word_arr)

# convert list of segments to word set of segment chunks


def toChunkWordSet(segments, num_per_chunk):
    return [segmentChunkToWordSet(chunk) for chunk in chunked(segments, num_per_chunk)]

# write all unique words in sentences to file


def wordsInSentencesToFile(punctless_sentences, memory_efficient=True):
    # for large dataset, use the memory efficient approach
    if memory_efficient:
        '''
        convert BOW to chunk only takes O(n) while merging two sets takes O(len(x)+len(y))
        for processing_batch_size = 100000
        no merging 500s, with chunk of 5 takes 230s, with chunk of 10 takes 170s, with chunk of 20 takes 138s
        for processing_batch_size = 300000
        with chunk of 20 takes 456s, chunk of 60 takes 356s, chunk of 100 takes 339s
        for processing_batch_size = 1000000
        reduce: with chunk of 100 takes 1200s, chunk of 300 takes 1087s, chunk of 1000 takes 1055s, chunk of 4000 takes 924s
        for loop: with chunk of 1000 takes 1277s, chunk of 4000 takes 1100s
        '''
        # collect all words to embed
        # join sentence together and convert to set before merging actually makes it faster
        chunk_word_sets = toChunkWordSet(punctless_sentences, 4000)
        # use reduce to make it faster
        words_to_embed = reduce(mergeOperator, chunk_word_sets)

        # the for loop approach
        # merging two sets takes O(len(x)+len(y)) thus slower for large sets
        '''
        words_to_embed = set([])
        for ps in punctless_sentences:
            words_to_embed = words_to_embed | set(ps.split())
        '''
    # if not, use the faster way
    else:
        # this is faster but uses much more memory
        words_to_embed = set(' '.join(punctless_sentences).split())

    print("embedding", len(words_to_embed), "words for this batch")
    writeWholeFile(temp_word_batch_fn, ' '.join(words_to_embed))

# get embedding LUT from fast text with sentences that has no punctuation


def getEmbeddingLUTFromFastText(punctless_sentences, fast_text_path, model_bin):
    # interestingly, if print here will cause a bug
    # since the function passed in a generator object, after
    # printing, generator becomes empty...
    # print(list(punctless_sentences))
    wordsInSentencesToFile(punctless_sentences)
    fast_text_embed_command = fast_text_path + \
        " print-word-vectors " + model_bin + " < " + temp_word_batch_fn
    ft_embeddings = subprocess.check_output(
        fast_text_embed_command, shell=True).decode()
    print("finish getting results from fast text")

    return fastTextOutputToLUT(ft_embeddings)


'''
This approach is indeed as fast as partial...
'''
# make RunEmbed an object to get around the pickle


class RunEmbed(object):
    def __init__(self, sentence_embedding, embeddingLUT,
                 do_normalize_word, do_normalize_sentence,
                 weighted_by_IDF,
                 default_IDF_weight,
                 spell_correct):
        self.sentence_embedding = sentence_embedding
        self.embeddingLUT = embeddingLUT
        self.do_normalize_word = do_normalize_word
        self.do_normalize_sentence = do_normalize_sentence
        self.weighted_by_IDF = weighted_by_IDF
        self.default_IDF_weight = default_IDF_weight
        self.spell_correct = spell_correct

    def __call__(self, sentence):
        self.sentence_embedding.embedSentenceWithEmbeddingLUT(sentence, self.embeddingLUT,
                                                              self.do_normalize_word, self.do_normalize_sentence,
                                                              self.weighted_by_IDF,
                                                              self.default_IDF_weight,
                                                              self.spell_correct)

# run multiprocessor embedding


def runEmbeddingLUTFromFastTextMP(sentence_embedding,
                                  sentences, embeddingLUT,
                                  do_normalize_word=True, do_normalize_sentence=True,
                                  weighted_by_IDF=True,
                                  default_IDF_weight=None,
                                  spell_correct=True):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_4) as pool:
        # declare an object to get around the pickle
        run_embed = RunEmbed(sentence_embedding, embeddingLUT,
                             do_normalize_word, do_normalize_sentence,
                             weighted_by_IDF,
                             default_IDF_weight,
                             spell_correct)
        sentence_vec_arr = pool.map(run_embed, sentences, 10000)
        pool.close()
        pool.join()

    return sentence_vec_arr
