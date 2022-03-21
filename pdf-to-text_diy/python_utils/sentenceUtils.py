from .preprocessing import *
from .embeddingUtils import *

# get axis for scoring


def getAxisForScoring(mat, short_side):
    # mode of calculating similarity (by averaging the
    # max similarity word match). if short_side, average
    # with respect to the shorter sentence, else, the longer
    mat_shape = mat.shape

    if short_side:
        # if average from the shorter side (with size argmin),
        # max from the longer side
        axis_use_for_scoring = np.argmax(mat_shape)
    else:
        # vice versa
        axis_use_for_scoring = np.argmin(mat_shape)

    return axis_use_for_scoring

# calculate the max sim score


def maxSimScore(sim_mat, weights, short_side):
    axis_use_for_scoring = getAxisForScoring(sim_mat, short_side)
    best_match_for_each_word = np.max(sim_mat, axis=axis_use_for_scoring)
    # weighted by weights
    return np.dot(best_match_for_each_word, weights)


# method used to calculate sentence similarity for sentences
# in vector representation


def vecArrSimilarity(vec_arr_1, vec_arr_2, short_side):
    vec_1_mat = np.row_stack(vec_arr_1)
    vec_2_mat = np.row_stack(vec_arr_2)

    sim_mat = cosine_similarity(vec_1_mat, vec_2_mat)

    return maxSimScore(sim_mat, short_side)

# extract common elements in two lists
# replacement determines whether the common should be removed


def extractCommon(list_1, list_2, replacement):
    # need to copy to prevent list_1 and 2 get changed
    # by remove
    l_1 = list_1.copy()
    l_2 = list_2.copy()

    common = []
    for e in l_1:
        if e in l_2:
            common.append(e)
            # l_2 needs to be remove in this loop
            l_2.remove(e)

    # search and remove needs to be separate,
    # or may cause skipping since the list shorten
    # during looping
    for e in common:
        l_1.remove(e)

    # if not remove from list, return original
    if replacement:
        return list_1, list_2, common

    return l_1, l_2, common


'''
calculate sentence similarity through word vectors
'''
'''
# calculate the similarity between sentences in BOW form
# short_sentence (short_side) determines the reference
# sentence for score calculation


def sentenceSimilarity(sentence_1, sentence_2,
                       embedding, short_sentence):
    # handle the case of same word in sentence 1 and 2
    # solve the edge case that the word is not embedded thus
    # cause the common word miscounted
    sentence_1, sentence_2, common = extractCommon(
        sentence_1, sentence_2, replacement=True)

    # if sentence all matched or one of them is empty, similarity = 1
    if min(len(sentence_1), len(sentence_2)) == 0:
        return 1

    # use the original sentence without removing the common words
    # here (i.e. replacement=True), since some other words can be similar
    # to the words in the common list
    vec_arr_1 = embedding.embedWords(sentence_1)
    vec_arr_2 = embedding.embedWords(sentence_2)

    # determine the divisor used in vecArrSimilarity
    if short_sentence:
        divisor = min(len(sentence_1), len(sentence_2))
    else:
        divisor = max(len(sentence_1), len(sentence_2))

    # number of common words
    num_common = len(common)
    # calculate the score without common words
    score_without_common = vecArrSimilarity(
        vec_arr_1, vec_arr_2, short_side=short_sentence)
    # calculate the final score with common words count as 1
    # (divisor - num_common) since the common words already
    # counted in the num_common correction
    score = (score_without_common * (divisor - num_common) +
             num_common) / divisor

    return score
'''

'''
calculate sentence similarity through similarity matrix
'''
# calculate the similarity between sentences in BOW form
# short_sentence (short_side) determines the reference
# sentence for score calculation
# word_weighting_func takes in an array of words and yield
# a weight vector with weight for each word


def sentenceSimilarity(sentence_1, sentence_2,
                       embedding, short_sentence,
                       word_weighting_func):
    # handle the case of same word in sentence 1 and 2
    # solve the edge case that the word is not embedded thus
    # cause the common word miscounted
    sentence_1, sentence_2, common = extractCommon(
        sentence_1, sentence_2, replacement=True)

    # if sentence all matched or one of them is empty, similarity = 1
    if min(len(sentence_1), len(sentence_2)) == 0:
        return 1

    # determine the divisor used in vecArrSimilarity
    if short_sentence:
        divisor = min(len(sentence_1), len(sentence_2))
    else:
        divisor = max(len(sentence_1), len(sentence_2))

    # which one is the divisor
    divisor_index = [len(sentence_1), len(sentence_2)].index(divisor)
    divisor_sentence = [sentence_1, sentence_2][divisor_index]

    # number of common words
    num_common = len(common)

    # if it's not none
    if word_weighting_func:
        # calculate the weights of each word
        weights = word_weighting_func(divisor_sentence)
        # calculate score for common words
        common_weights = word_weighting_func(common)
        common_score = np.sum(common_weights)
    else:
        # else, equal weights
        weights = np.array([1 / divisor] * divisor)
        # score for common words is the number of common words
        common_score = num_common

    sim_mat = embedding.listToListSimilarities(
        sentence_1, sentence_2)

    score_without_common = maxSimScore(
        sim_mat, weights, short_side=short_sentence)

    # calculate the final score with common words count as 1
    # (divisor - num_common) since the common words already
    # counted in the num_common correction
    score = (score_without_common * (divisor - num_common) +
             common_score) / divisor

    return score

# sentence database for similar sentence look up


class SentenceDatabase:
    def __init__(self, database, embedding,
                 remove_subject=True, cleanse_sentence=True,
                 use_stemmer="none", stop_words_option="small"):

        database = self.tokenizeAndRemove(database)
        self.database = self.curateDatabase(database,
                                            remove_subject=remove_subject,
                                            cleanse_sentence=cleanse_sentence,
                                            use_stemmer=use_stemmer,
                                            stop_words_option=stop_words_option)
        self.original_sentences = database
        self.embedding = embedding
        print("database constructed:", self.database)

    # tokenize and remove sentences with too many NN JJ

    def tokenizeAndRemove(self, database):
        # if no inputting None as sentences, return None
        # and keep DB in uninitialized state
        if database is None:
            return None

        # if the input is string, convert to tokens
        if isinstance(database[0], str):
            database = tokenizeArr(database)

        database = filterTooManyNNJJs(database, 15)

        return database

    # convert list of sentences into sentence database

    def curateDatabase(self, sentences,
                       remove_subject, cleanse_sentence,
                       use_stemmer, stop_words_option):
        # if no inputting None as sentences, return None
        # and keep DB in uninitialized state
        if sentences is None:
            return None

        database = sentences

        # remove the subjects to construct the sentence database
        if remove_subject:
            database = removeSubjectArr(database)

        # cleansing needs to be done after the remove subject
        # or the missing the, be and pronoun can confuse the
        # algorithm
        if cleanse_sentence:
            database = replaceBeArr(database, "be")
            database = replacePronounArr(database, "P_R_O_N_O_U_N")

        # remove all stop words according to command
        if stop_words_option.lower() == "whole":
            print("use the whole stopwords list")
            database = filterWordsInListArr(database, stop_words_whole)
        elif stop_words_option.lower() == "small":
            print("use the small stopwords list")
            database = filterWordsInListArr(database, determiners)
        else:
            print("use no stopwords list")

        # stemming
        if use_stemmer.lower() == "porter":
            print("use porter stemmer for database")
            database = stemWordsArr(database, porter_stemmer)
        elif use_stemmer.lower() == "snowball":
            print("use snowball stemmer for database")
            database = stemWordsArr(database, snowball_stemmer)
        elif use_stemmer.lower() == "snowball_ignore_stop":
            print("use snowball stemmer that ignores stop word for database")
            database = stemWordsArr(database, snowball_stemmer_ignore_stop)
        elif use_stemmer.lower() == "none":
            print("use no stemmer for database")
        else:
            print(
                "cannot recognize your option, use default (use no stemmer) for database")

        return database

    # function that saves the database into file

    def saveDatabase(self, fn):
        writeBOWs(self.database, fn)

    # function that load database into the class

    def loadDatabase(self, fn):
        self.database = readDB(fn)

    # calculate sentence similarity using the embedding in class

    def sentenceSimilarityUnderEmbedding(self,
                                         sentence_1, sentence_2,
                                         word_weighting_func,
                                         short_sentence):
        return sentenceSimilarity(sentence_1, sentence_2,
                                  self.embedding,
                                  word_weighting_func=word_weighting_func,
                                  short_sentence=short_sentence)

    def compareToDatabase(self, sentence, word_weighting_func=None, short_sentence=True):
        # initialize table
        similarity_table = pd.DataFrame(
            columns=["original sentence", "similarity to input", "next sentence"])
        for i in range(0, len(self.database)):
            ref_sentence = self.database[i]
            its_original_sentence = BOWToDoc(self.original_sentences[i])

            if (i + 1) < len(self.database):
                its_next_sentence = BOWToDoc(self.original_sentences[i+1])
            else:
                its_next_sentence = "None"

            its_original_sentence = checkAndJoin(its_original_sentence)
            its_next_sentence = checkAndJoin(its_next_sentence)

            similarity_table.loc[' '.join(ref_sentence)] = [its_original_sentence, self.sentenceSimilarityUnderEmbedding(
                sentence, ref_sentence, word_weighting_func=word_weighting_func,
                short_sentence=short_sentence), its_next_sentence]

        return similarity_table.sort_values(by="similarity to input", ascending=False)

    # Helper function for compare to database multi processor version
    def compareToDatabaseHelper(self, i, sentence,  word_weighting_func, short_sentence):
        ref_sentence = self.database[i]
        its_original_sentence = self.original_sentences[i]

        if (i + 1) < len(self.database):
            its_next_sentence = self.original_sentences[i+1]
        else:
            its_next_sentence = "None"

        its_original_sentence = checkAndJoin(its_original_sentence)
        its_next_sentence = checkAndJoin(its_next_sentence)

        name = ' '.join(ref_sentence)
        vals = [its_original_sentence, self.sentenceSimilarityUnderEmbedding(
                sentence, ref_sentence, word_weighting_func=word_weighting_func,
                short_sentence=short_sentence), its_next_sentence]

        return (name, vals)

    # multiprocessor version of compare to DB
    def compareToDatabaseMP(self, sentence, word_weighting_func=None, short_sentence=True):
        # use parallelism to speed up, use 1000 as chunk size
        with eval(core_pool_8) as pool:
            compare_results = pool.map(partial(self.compareToDatabaseHelper,
                                               sentence=sentence, word_weighting_func=word_weighting_func,
                                               short_sentence=short_sentence), range(0, len(self.database)), 1000)

        columns = ["original sentence", "similarity to input", "next sentence"]
        index = []
        data = []

        for name, vals in compare_results:
            index.append(name)
            data.append(vals)

        similarity_table = pd.DataFrame(
            index=index, columns=columns, data=data)
        return similarity_table.sort_values(by="similarity to input", ascending=False)


'''
def test_vecArrSimilarity():
    a = np.array([
        [1,2,3,4],
        [0,0.1,0,0],
        [2,1,7,10],
        [1,1,1,1]
    ])

    b = np.array([
        [0,3,1,1],
        [1,1,1,1],
        [1,2,3,4],
        [1,1,1,1],
        [1,1,0,0]
    ])

    print(cosine_similarity(a, b))
    print(vecArrSimilarity(a, b, short_side=True))
    print(vecArrSimilarity(a, b))
    print(vecArrSimilarity(a, b, short_side=False))


test_vecArrSimilarity()
'''

'''
def test_sentenceSimilarity():
    embedding_data = pd.read_pickle(
        "embeddings_without_stemming_large_dataset/PPMI_paper_word_embedding_500SVD.pkl")
    embedding = Embedding(embedding_data)

    sen_1 = ["arm", "chromosomes", "centromere"]
    sen_2 = ["arm", "chromosomes", "how", "necessary"]

    for w_1 in sen_1:
        for w_2 in sen_2:
            print(w_1, w_2)
            print(embedding.checkSimilarityBetween(w_1, w_2))

    print("sim from short: ", sentenceSimilarity(
        sen_1, sen_2, embedding, short_sentence=True))

    for w_1 in sen_2:
        for w_2 in sen_1:
            print(w_1, w_2)
            print(embedding.checkSimilarityBetween(w_1, w_2))

    print("sim from long: ", sentenceSimilarity(
        sen_1, sen_2, embedding, short_sentence=False))

    # edge case where word is not in embed
    g = embedding.embedWord("chromosomes")
    h = embedding.embedWord("chmosomes")
    print(cosine_similarity(g.reshape(1,-1), h.reshape(1,-1)))


test_sentenceSimilarity()
'''

'''
def test_sentenceSimilarity_2():
    embedding_data = pd.read_pickle(
        "embeddings_without_stemming_large_dataset/PPMI_paper_word_embedding_500SVD.pkl")
    embedding = Embedding(embedding_data)
    sen_1 = ['DEPARTMENT', 'OF', 'MICROBIOLOGY', 'AND', 'IMMUNOLOGY', 'FACULTY', 'POSITIONS', 'University', 'Maryland', 'School', 'Medicine', 'Baltimore', 'Maryland', 'The', 'Department', 'Microbiology', 'Immunology', 'University', 'Maryland',
             'School', 'Medicine', 'http', 'medschool.umaryland.edu', 'Microbiology', 'recruiting', 'new', 'established', 'investigators', 'active', 'R01', 'K-Award', 'equivalent', 'funded', 'research', 'programs', 'host-pathogen', 'interactions']
    print(sentenceSimilarity(sen_1, sen_1,
                             embedding, short_sentence=True))


test_sentenceSimilarity_2()
'''

'''
def test_compareToDatabase():
    embedding_data = pd.read_pickle(
        "embeddings_without_stemming_large_dataset/PPMI_paper_word_embedding_500SVD.pkl")
    embedding = Embedding(embedding_data)

    sen_1 = ["arm", "chromosomes", "centromere"]
    sen_2 = ["arm", "chromosomes", "how", "necessary"]
    sen_3 = ["centromere", "while", "when"]

    database = [sen_1, sen_2, sen_3]

    SDB = SentenceDatabase(database=database, embedding=embedding)

    print(SDB.compareToDatabase(sen_2))


test_compareToDatabase()
'''

'''
def test_extractCommon():
    l_1 = [1, 2, 3, 4, 5, 10, 9, 11, 22, 21, 1]
    l_2 = [5, 6, 9, 1, 0, 2]

    m_1, m_2, c = extractCommon(l_1, l_2, False)
    print("extractCommon(l_1, l_2, False)")
    print(m_1)
    print(m_2)
    print(c)
    print(l_1)
    print(l_2)

    m_2, m_1, c = extractCommon(l_2, l_1, False)
    print("extractCommon(l_2, l_1, False)")
    print(m_1)
    print(m_2)
    print(c)
    print(l_1)
    print(l_2)


test_extractCommon()
'''

'''
def test_sentence_class_new():
    database = [
        "Biology watches a movie and sleep",
        "Chromosome is a very important thing",
        "The biology watches a movie and sleep",
        "Chromosome is a very important thing the the is are",
        "A flying dog",
        "A flying dog is watching five movies",
        "I like cookie"
    ]

    print("F F N")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=False,
        cleanse_sentence=False,
        use_stemmer="None")

    print("F T N")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=False,
        cleanse_sentence=True,
        use_stemmer="None")

    print("T T N")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=True,
        cleanse_sentence=True,
        use_stemmer="None")

    print("T F N")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=True,
        cleanse_sentence=False,
        use_stemmer="None")

    print("F F P")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=False,
        cleanse_sentence=False,
        use_stemmer="porter")

    print("F F S")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=False,
        cleanse_sentence=False,
        use_stemmer="snowball")

    print("T F P")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=True,
        cleanse_sentence=False,
        use_stemmer="porter")

    print("T T S")
    sentence_database = SentenceDatabase(
        database, None,
        remove_subject=True,
        cleanse_sentence=True,
        use_stemmer="snowball")


test_sentence_class_new()
'''
