import math
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

from .preprocessing import *
from .gramHelper import *


def log2_and_1(a): return math.log2(a + 1)

# for each type of gram, construct the vector


def senToVecEachGram(cur_gram_list, cur_sen_gram, transform):
    cur_vec = []

    # loop through the grams
    for i in range(0, len(cur_gram_list)):
        gram = cur_gram_list[i]

        # if the gram is not in the sentence, append 0
        # and go to the next gram
        if gram not in cur_sen_gram.keys():
            cur_vec.append(0)
            continue

        cur_vec.append(transform(cur_sen_gram[gram]))

    return cur_vec

# convert sentence to vector of gram features


def senToVec(sen, gram_dict, use, transform):
    sen_uni = textToBOW(sen)
    sen_bi = BOWToBigram(sen_uni)
    sen_tri = BOWToTrigram(sen_uni)

    sen_dict = {
        'unigram': Counter(sen_uni),
        'bigram': Counter(sen_bi),
        'trigram':  Counter(sen_tri)
    }

    sen_vec = []

    for i in range(0, len(use)):
        g_ID = use[i]

        cur_gram_list = gram_dict[g_ID]
        cur_sen_gram = sen_dict[g_ID]

        cur_vec = senToVecEachGram(cur_gram_list, cur_sen_gram, transform)

        sen_vec.extend(cur_vec)

    return np.array(sen_vec)

# convert list of sentence into gram feature matrix


def senListToMat(sen_list, gram_dict, use=['unigram', 'bigram', 'trigram'], transform=log2_and_1):
    sen_mat = []

    for i in range(0, len(sen_list)):
        sen = sen_list[i]
        sen_vec = senToVec(sen, gram_dict, use, transform)
        sen_mat.append(sen_vec)

    return np.array(sen_mat)


def calcCosDistMat(sen_mat):
    sparse_sen_mat = sparse.csr_matrix(sen_mat)
    sen_csm = cosine_similarity(sparse_sen_mat)
    sen_cdm = 1 - sen_csm

    return sen_cdm

'''
def test_senToVec():
    a = "a man is a h s a e d qw a s da d a fa mi e"
    b = "a"
    c = "a happy man"
    d = "a good man a man e a e d qw a"
    gram_dict = {
        'unigram': ['a', 'man', 'e'],
        'bigram': ['a man', 'a e'],
        'trigram': ['a man a', 'a s da', 'd qw a']
    }

    print(senListToMat([a, b, c, d], gram_dict))

test_senToVec()
'''
