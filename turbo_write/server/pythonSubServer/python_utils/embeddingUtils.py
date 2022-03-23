from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

# symmetrize a matrix


def symmetrize(mat):
    dimension = len(mat)
    sim_mat = np.zeros(shape=[dimension, dimension])
    # make mat[i,j] = mat[j,i] = (mat[i,j] + mat[j,i]) / 2
    for i in range(0, dimension):
        for j in range(i, dimension):
            ij_avg = (mat[i, j] + mat[j, i]) / 2
            sim_mat[i, j] = ij_avg
            sim_mat[j, i] = ij_avg

    return sim_mat

# calculate value to adjust the similarity to


def findMaxAdjustment(val):
    # if the similarity > 0.95, don't need to adjust
    if val > 0.95:
        return val

    # else, adjust according to the similarity values
    if val > 0.6:
        return 0.95
    elif val > 0.5:
        return 0.9
    elif val > 0.4:
        return 0.8
    elif val > 0.35:
        return 0.7
    elif val > 0.3:
        return 0.6
    elif val > 0.25:
        return 0.5
    elif val > 0.2:
        return 0.4
    elif val > 0.15:
        return 0.3
    else:
        return 0.2

# find second largest in the array


def findSecondLargest(arr):
    return sorted(arr, reverse=True)[1]

# adjust the weights of similarity matrix


def adjustSimilarities(sim_mat):
    dimension = len(sim_mat)
    adjusted_mat = np.zeros(shape=[dimension, dimension])
    for i in range(0, dimension):
        row_i = sim_mat[i]
        # determine adjustment factor based on second
        # largest value
        second_largest = findSecondLargest(row_i)

        # skip in case of zero
        if second_largest == 0:
            continue

        adjustment = findMaxAdjustment(second_largest)
        adjustment_factor = adjustment / second_largest
        # adjust
        adjusted_mat[i] = row_i * adjustment_factor

    # set the max to 1
    adjusted_mat[adjusted_mat > 1] = 1
    # symmetrize
    adjusted_mat = symmetrize(adjusted_mat)

    return adjusted_mat


# a class for analyzing the quality of embedding
# and embed words


class Embedding:
    def __init__(self, embedding, adjust_sim=False):
        self.embedding = embedding
        self.adjust_sim = adjust_sim

        # dimension of the embedding
        self.dimension = embedding.shape[1]
        self.embedding = self.addNotEmbedded(self.embedding)
        self.similarity_mat = self.calcSimMatrix()

    # add not embeded column into the embedding table
    def addNotEmbedded(self, embedding):
        # create a copy
        # if temp = embedding, then the operation is done on
        # the original object. Thus use a copy
        temp = embedding.copy()
        temp.loc["not_embedded"] = [0.0] * self.dimension
        return temp

    # calculate the cosine similarity matrix

    def calcSimMatrix(self):
        similarity_mat = cosine_similarity(self.embedding)

        # adjust similarity if set
        if self.adjust_sim:
            similarity_mat = adjustSimilarities(similarity_mat)

        similarity_mat = pd.DataFrame(
            data=similarity_mat,
            index=self.embedding.index,
            columns=self.embedding.index
        )
        return similarity_mat

    # map the unembedded word to "not_embedded"

    def wordGuard(self, word, show_not_found=False):
        if word not in self.embedding.index:
            if show_not_found:
                print("word " + word +
                      " is not embedded, use default all 0 value for its embedding")
            return "not_embedded"

        return word

    # show the similarity of a word with other words sorted
    # by cosine similarity

    def checkSimilarities(self, word):
        # in case word not embedded
        word = self.wordGuard(word)

        return self.similarity_mat[word].sort_values(ascending=False)

    # show the similarity of a word with another word

    def checkSimilarityBetween(self, word_1, word_2):
        # in case word not embedded
        word_1 = self.wordGuard(word_1)
        word_2 = self.wordGuard(word_2)

        return self.similarity_mat.at[word_1, word_2]

    def listToListSimilarities(self, list_1, list_2):
        # in case words not embedded
        list_1 = [self.wordGuard(w) for w in list_1]
        list_2 = [self.wordGuard(w) for w in list_2]

        return self.similarity_mat.loc[list_1, list_2]

    # method to turn word into vector

    def embedWord(self, word):
        # convert to lower case
        word = word.lower()
        # in case word not embedded
        word = self.wordGuard(word)

        vec = self.embedding.loc[word]
        return np.array(vec)

    def embedWords(self, words):
        vec_arr = [self.embedWord(words[i]) for i in range(0, len(words))]
        return vec_arr


'''
def test_Embedding():
    embedding_data = pd.read_pickle(
        "embeddings_without_stemming_large_dataset/PPMI_paper_word_embedding_500SVD.pkl")
    embedding = Embedding(embedding_data)
    print(embedding.embedding)
    print(embedding.similarity_mat)

    w = "sdafasdfasdf"
    x = "yusidofhioasudfuh"
    u = "chromosome"
    y = "chromosomes"

    v = embedding.embedWord(w)
    print("w: ", w)
    print("v: ", v)

    print("w check: ", embedding.checkSimilarities(w))
    print("u check: ", embedding.checkSimilarities(u))

    print("w u check: ", embedding.checkSimilarityBetween(w, u))
    print("w x check: ", embedding.checkSimilarityBetween(w, x))
    print("y x check: ", embedding.checkSimilarityBetween(y, x))
    print("u y check: ", embedding.checkSimilarityBetween(u, y))

    # make sure that the operation didn't change the input
    print("w, x, u, y: ", w, x, u, y)


test_Embedding()
'''

'''
def test_symmetrize():
    a = np.array(range(0, 9)).reshape(3, 3)
    b = np.array(range(0, 100)).reshape(10, 10)
    print(symmetrize(a))
    print(symmetrize(b))

test_symmetrize()
'''

'''
def test_adjustment():
    embedding_data = pd.read_pickle(
        "embeddings/PPMI_None_small_paper_word_embedding_1000SVD.pkl")
    embedding = Embedding(embedding_data)
    sim_mat = embedding.similarity_mat
    for i in range(0, len(sim_mat)):
        print(sim_mat.iloc[i].sort_values(ascending=False))

test_adjustment()
'''
