import numpy as np
from numpy.linalg import norm
from numba import jit, prange
import pandas as pd

from math import log2

from scipy.sparse import csr_matrix, issparse

from sklearn.random_projection import johnson_lindenstrauss_min_dim, GaussianRandomProjection, SparseRandomProjection

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils.extmath import randomized_svd
from sklearn.decomposition import TruncatedSVD

from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

from .stopWords import *

infinity = float("inf")
negative_infinity = float("-inf")


def normalizeVector(vec):
    # when default (ord=None in norm), equal to ord=2
    vec_len = norm(vec)
    if vec_len > 0:
        return vec / vec_len

    # if length 0, return the original vec
    return vec

# lookup the elements in values that have
# the indices in lookup


def indexLookup(values, lookup):
    return [values[lookup[i]] for i in range(0, len(lookup))]

# convert documents into count matrix


def toCountMat(docs, min_df, tokenizer):
    # ngram_range=(1, 1) only uses unigram
    vectorizer = CountVectorizer(ngram_range=(
        1, 1), min_df=min_df, tokenizer=tokenizer)
    doc_vecs = vectorizer.fit_transform(docs)
    return vectorizer.get_feature_names(), doc_vecs

# convert documents into co-occurence matrix


def toCoocMat(docs, min_df, tokenizer, in_freq):
    words, count_mat = toCountMat(docs, min_df, tokenizer=tokenizer)
    '''
    since most words occur only once in a sentence,
    this matrix multiplication is equal to cooc matrix
    this is equal to np.matmul(count_mat.T, count_mat)
    since it is sparse matrix
    '''
    cooc_mat = count_mat.T * count_mat

    # if in_freq, turn occurrence into frequency,
    # else, keep in counts
    if in_freq:
        doc_num = len(docs)
        cooc_mat = cooc_mat / doc_num

    return words, cooc_mat

# helper function for PMI calculation


def calcPMIValue(cooc_mat, i, j, positive):
    if cooc_mat[i, j] == 0:
        PMI_value = negative_infinity
    else:
        log2_i = log2(cooc_mat[i, i])
        log2_j = log2(cooc_mat[j, j])
        log2_i_and_j = log2(cooc_mat[i, j])
        # use minus instead of division
        # to prevent underflow
        PMI_value = log2_i_and_j - log2_i - log2_j

    # if need PPMI
    if positive:
        PMI_value = max(0, PMI_value)

    return PMI_value

# convert documents into PMI matrix
# choose positive=True for PPMI
# speed up with parallelism


def toPMIMat(docs, min_df, tokenizer, positive=True):
    # to calculate PMI, must use freq for cooc_mat
    words, cooc_mat = toCoocMat(
        docs, min_df, tokenizer=tokenizer, in_freq=True)

    # get shape of matrix
    matrix_shape = cooc_mat.shape
    row_size = matrix_shape[0]
    col_size = matrix_shape[1]

    '''
    no need for inplace calculation of PMI, since
    in this app, num of words are small and inplace
    may induce bug due to racing condition, can improve
    to inplace later
    '''
    # initialization
    PMI_mat = np.zeros(shape=matrix_shape)

    # accessing dense matrix is much faster than sparse matrix
    # about 600 times for 1300 * 1300 matrix...
    cooc_mat = cooc_mat.todense()

    for i in prange(0, row_size):
        for j in range(0, col_size):
            PMI_mat[i, j] = calcPMIValue(cooc_mat, i, j, positive)

    return words, PMI_mat


# convert documents into tfidf matrix


def toTFIDFMat(docs, min_df, tokenizer=None):
    vectorizer = TfidfVectorizer(
        min_df=min_df, tokenizer=tokenizer, use_idf=True, smooth_idf=True, sublinear_tf=False)
    doc_vecs = vectorizer.fit_transform(docs)
    return vectorizer.get_feature_names(), doc_vecs

# get the IDF information (vocab, stop words, idf)
# TfidfVectorizer will automatically remove single characters (a, b, c...) even without providing any
# stop words


def calcIDFInfo(docs, min_df, stop_words=set([]), tokenizer=None):
    vectorizer = TfidfVectorizer(
        min_df=min_df, tokenizer=tokenizer, stop_words=stop_words, use_idf=True, smooth_idf=True)
    IDF_info = vectorizer.fit(docs)
    # all stop words are the merge of two
    total_stop_words = IDF_info.stop_words_ | stop_words
    return len(docs), IDF_info.vocabulary_, total_stop_words, IDF_info.idf_


# perform truncated svd on data
# since SVD depends on variance not mean,
# truncatedSVD yields the same result as SVD but
# applicable to sparse data


def SVDEmbedding(mat, n_components, n_iter=10):
    # calculate the embedding U as shown in the
    # Inducing Domain-Specific Sentiment Lexicons from
    # Unlabeled Corpora paper as embedding
    U, Sigma, VT = randomized_svd(
        mat, n_components=n_components, n_iter=n_iter)

    mat_transformed = U * Sigma
    exp_var = np.var(mat_transformed, axis=0)

    # check whether sparse
    if issparse(mat):
        # if it is, convert to dense before computing var
        full_var = np.var(mat.todense(), axis=0).sum()
    else:
        full_var = np.var(mat, axis=0).sum()

    explained_variance_ratio = exp_var / full_var

    print("Each variance explains variance: ")
    print(explained_variance_ratio)
    print("In total: ")
    print(sum(explained_variance_ratio))

    # the transformation in TruncatedSVD uses U * sigma, but
    # researches have shown that excluding sigma yields better
    # results ("Inducing Domain-Specific Sentiment Lexicons from
    # Unlabeled Corpora")
    return U

# use SVD for dimension reduction


def SVDReduction(mat, n_components, n_iter=10):
    # check for case which number of features <= dimension
    if mat.shape[1] <= n_components:
        print("# dim < n_components, no need for dimension reduction.")
        return mat

    svd = TruncatedSVD(n_components=n_components, n_iter=n_iter)
    svd.fit(mat)

    explained_variance_ratio = svd.explained_variance_ratio_
    print("Each variance explains variance: ")
    print(explained_variance_ratio)
    print("In total: ")
    print(sum(explained_variance_ratio))

    return svd.transform(mat)

# use random projection for dimension reduction


def RPReduction(mat, n_components='auto', density='auto', eps=0.1,
                sparse=True):
    # if n_components is determined by auto
    if n_components == 'auto':
        n_s = mat.shape[0]
        n_f = mat.shape[1]
        min_dim = johnson_lindenstrauss_min_dim(n_samples=n_s, eps=eps)
        if min_dim > n_f:
            print("johnson_lindenstrauss_min_dim (" +
                  str(min_dim) +
                  ") is greater than the number of features (" +
                  str(n_f) +
                  "), skip random projection")
            return mat

    if sparse:
        RP = SparseRandomProjection(
            n_components=n_components, density=density, eps=eps)
    else:
        RP = GaussianRandomProjection(n_components=n_components, eps=eps)

    # fit the random matrix
    RP.fit(mat)

    return RP.transform(mat)

# run k means clustering on data


def KMeansClustering(data, n_clusters, n_jobs=4, algorithm="full"):
    # check for case which number of data < number of clusters
    if len(data) < n_clusters:
        n_clusters = len(data)

    k_means = KMeans(n_clusters=n_clusters, n_jobs=n_jobs, algorithm=algorithm)
    k_means.fit(data)

    return k_means


def AGClustering(data, n_clusters, metric, linkage_criteria):
    # check for case which number of data < number of clusters
    if len(data) < n_clusters:
        n_clusters = len(data)

    Agglomerative = AgglomerativeClustering(
        n_clusters=n_clusters, linkage=linkage_criteria, affinity=metric)
    Agglomerative.fit(data)

    return Agglomerative

# gather the index of members in each cluster


def clusterMember(clustering):
    return {
        i: [index for index, val in enumerate(clustering.labels_) if val == i] for i in range(clustering.n_clusters)
    }

# take in data and already run clustering,
# return a set of data divided into subgroups


def divideDataByCluster(data, clustering):
    return {
        i: data[np.where(clustering.labels_ == i)] for i in range(clustering.n_clusters)
    }

# divide the similarity matrix by the cluster of their members


def divideSimMatByCluster(sim_mat, member_dict):
    SimMat_dict = {}
    for key in member_dict.keys():
        members = member_dict[key]
        SimMat_dict[key] = sim_mat[np.ix_(members, members)]

    return SimMat_dict


# calculate similarity matrix from array of data points


def toSimMatrix(data, sim_fun):
    num_data = len(data)
    sim_mat = np.zeros(shape=[num_data, num_data])
    for i in prange(0, num_data):
        for j in range(i, num_data):
            i_j_sim = sim_fun(data[i], data[j])
            sim_mat[i, j] = i_j_sim
            sim_mat[j, i] = i_j_sim

    return sim_mat

# find the center of the data by selecting the one with
# largest sum of its similarity values to others


def getCenter(sim_mat):
    sum_sim = np.sum(sim_mat, axis=1)
    return np.argmax(sum_sim)


'''
def test_toPMIMat():
    sentences = [
        "aqq bqq",
        "bqq aqq",
        "aqq bqq",
        "aqq bqq",
        "cqq dqq",
        "cqq dqq",
        "cqq dqq",
        "aqq cqq"
    ]
    words, PPMI = toPMIMat(sentences, min_df=0, positive=True)
    print("words: \n", words)
    print("PPMI: \n", PPMI)
    words, PMI = toPMIMat(sentences, min_df=0, positive=False)
    print("words: \n", words)
    print("PMI: \n", PMI)


test_toPMIMat()
'''

'''
def test_divideDataByCluster():
    a = np.array([[1], [1], [1.2], [55], [1.1], [1.5], [49], [47]])
    clustering = KMeansClustering(a, 2, algorithm="full")
    clusters = divideDataByCluster(a, clustering)
    print(clusters)


test_divideDataByCluster()
'''

'''
def test_divideDataByCluster():
    a = np.array([[1], [1], [1.2], [55], [1.1], [1.5], [49], [47]])
    clustering = KMeansClustering(a, 2, algorithm="full")
    clusters = clusterMember(clustering)
    print(clusters)


test_divideDataByCluster()
'''

'''
def test_getCenter():
    a = np.array([
        [1, 0.8, 0.4],
        [1, 0.8, 0.4],
        [1, 0.99, 0.55],
        [1, 0.97, 0.75],
        [1, 0.8, 0.4],
        [1, 0.2, 0.1],
        [1, 0.9, 0.7],
    ])

    b = np.array([
        [1, 0.8, 0.4],
        [1, 0.8, 0.4],
        [1, 0.2, 0.1],
        [1, 0.9, 0.2],
        [1, 0.99, 0.55]
    ])

    print(getCenter(a))
    print(getCenter(b))

test_getCenter()
'''

'''
def test_indexLookup():
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    b = [5, 0, 3, 2]

    print(indexLookup(a, b))

test_indexLookup()
'''
