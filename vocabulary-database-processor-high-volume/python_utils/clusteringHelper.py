import numpy as np
import sklearn
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

from .tfVectorization import *

# PCA transform the data


def PCATransform(data, num_PC):
    pca = PCA(n_components=num_PC)
    pca.fit(data)
    print("PCA ratio: ", np.cumsum(pca.explained_variance_ratio_))
    return pca.fit_transform(data)

# run Kmeans on data


def runKmeans(data, num_clus):
    sentences_kmeans = KMeans(n_clusters=num_clus, random_state=0)
    sentences_kmeans.fit(data)
    return sentences_kmeans

# separate data that belongs to different cluster


def dispatchClusters(data, labels):
    data_dict = {}
    label_dict = {}
    for i in range(0, len(labels)):
        l = labels[i]

        # collect sentences and their neighbors
        if i == 0:
            sentence_and_neighbor = ['', data[i], data[i + 1]]
        elif i == len(labels) - 1:
            sentence_and_neighbor = [data[i - 1], data[i], '']
        else:
            sentence_and_neighbor = [data[i - 1], data[i], data[i + 1]]

        if l not in data_dict.keys():
            data_dict[l] = [sentence_and_neighbor]
            label_dict[l] = [i]
        else:
            data_dict[l].append(sentence_and_neighbor)
            label_dict[l].append(i)

    return label_dict, data_dict

# find the center sentence (one with the least square sum from other
# members)


def centerSentence(sentences, feature_mat, label_clus, calc_dist_mat=False):
    # decide whether distance mat need to be calc
    if calc_dist_mat:
        dist_mat = calcCosDistMat(feature_mat)
    else:
        dist_mat = feature_mat

    center_dict = {}

    cluster_ID = label_clus.keys()
    for ID in cluster_ID:
        label = label_clus[ID]

        # extract the submatrix and square
        sub_mat = dist_mat[label]
        sub_mat = sub_mat[:, label]
        sub_mat_sq = np.square(sub_mat)

        # find sentence that have min sum square dist
        dist_sum_mat = np.sum(sub_mat_sq, axis=1)
        center_index = np.argmin(dist_sum_mat)
        center_label = label[center_index]
        center_sentence = sentences[center_label]

        center_dict[ID] = center_sentence

    return center_dict
