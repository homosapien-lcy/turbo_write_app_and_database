import time
from joblib import Parallel, delayed

from .embeddingUtils import *
from .numericalAnalysisUtils import *


# run layerwiseDivision for a single leaf
# first layer is whether the division is first layer
# which determines parallelism
def runLeafLayerwiseDivision(leaf, leaf_sim_mat,
                             clustering_lambda, rest_num_layers,
                             first_layer):
    # recursive call to the leaves
    leaf.layerwiseDivision(sim_mat=leaf_sim_mat,
                           clustering_lambda=clustering_lambda,
                           num_layers=rest_num_layers,
                           first_layer=first_layer)


# a sentence node contains a value (sentence)
# and a list of leaves (sentence nodes)
'''
it is designed to hold the index of the sentences in the
original database other than the sentences themselves to make 
clustering and lookup easier.
all index refers to the index in the original database other
than the relative index in the particular database layer
'''


class DataNode:
    def __init__(self, leaves_ind):
        # center_ind is the index of the center of this cluster
        # in the original database
        self.center_ind = None
        # contains the indices of all members in the original
        # database of this cluster (which is all member in its
        # leaves combined)
        self.leaves_ind = leaves_ind
        # contains the indices of each cluster members in the original
        # database, keys by leaf id (cluster), initialize as None
        self.leaves_ind_dict = None
        # leaves is a dict that contains nodes, initialize as None
        self.leaves = None
        # a boolean to record whether the node has going through
        # leaf division, start as False
        self.is_divided = False

    def setCenter(self, sim_mat):
        # if sim_mat is empty
        if len(sim_mat) <= 0:
            print("empty similarity matrix")
            self.center_ind = None
        else:
            self.center_ind = self.leaves_ind[getCenter(sim_mat)]

    # divide leaves into clusters by sim_mat
    def divideLeaves(self, sim_mat, clustering_lambda):
        # generate from similarty matrix clustering
        clustering = clustering_lambda(sim_mat)
        # get the members of each cluster
        member_dict = clusterMember(clustering)
        # divide the similarity matrix
        sim_mat_dict = divideSimMatByCluster(sim_mat, member_dict)

        leaves_ind_dict = {}
        leaves = {}
        for key in member_dict.keys():
            # find the leaves_ind of this leaf
            # the relative indices of members of a leaf
            leaf_leaves_ind_relative = member_dict[key]
            leaf_leaves_ind = indexLookup(
                self.leaves_ind, leaf_leaves_ind_relative)

            # construct leaf
            leaf = DataNode(leaves_ind=leaf_leaves_ind)

            # set center_ind of leaf
            leaf_sim_mat = sim_mat_dict[key]
            leaf.setCenter(leaf_sim_mat)

            # fill the results needed by the node itself
            leaves_ind_dict[key] = leaf_leaves_ind
            leaves[key] = leaf

        # fill the results needed by the node itself
        self.leaves_ind_dict = leaves_ind_dict
        self.leaves = leaves
        self.is_divided = True

        # return the similarity matrix dictionary for
        # recursive division
        return sim_mat_dict

    # layerwise clustering takes in data and a cluster lambda method
    # (which takes in data only) and ouputs clusters and divide data
    # into layers of clusters

    def layerwiseDivision(self, sim_mat, clustering_lambda,
                          num_layers,
                          n_jobs=4,
                          first_layer=False):
        # if the rest of layers <= 1 or sim_mat is empty, stop
        if num_layers <= 1 or len(sim_mat) <= 0:
            print("this branch of division is finished")
            return

        print("simlarity matrix: ")
        print(sim_mat)

        # self divide
        sim_mat_dict = self.divideLeaves(sim_mat, clustering_lambda)

        # calculate the rest number of division needed
        rest_num_layers = num_layers - 1

        # parallel processing cannot handle nest
        # only run parallel in the first layer
        if first_layer:
            # only backend=threading works, the default backend option
            # does not divide beyond the first layer
            Parallel(n_jobs=n_jobs, backend="threading", verbose=0)(
                delayed(runLeafLayerwiseDivision)(self.leaves[key], sim_mat_dict[key],
                                                  clustering_lambda, rest_num_layers,
                                                  False)
                for key in sim_mat_dict.keys())
        # for later layers, use sequential
        else:
            for key in sim_mat_dict.keys():
                # retrieve sim_mat for the leaf and leaf node
                leaf_sim_mat = sim_mat_dict[key]
                leaf = self.leaves[key]

                # recursive call to the leaves
                leaf.layerwiseDivision(sim_mat=leaf_sim_mat,
                                       clustering_lambda=clustering_lambda,
                                       num_layers=rest_num_layers,
                                       first_layer=False)

    # print the info of this node and its leaves
    def printInfo(self):
        print("center_id:", self.center_ind)
        print("leaves_ind:", self.leaves_ind)
        print("leaves_ind_dict:", self.leaves_ind_dict)
        print("leaves:", self.leaves)
        print("is_divided:", self.is_divided)

        if self.leaves != None:
            for key in self.leaves.keys():
                print("its leaf # " + str(key) + " contains:")
                leaf = self.leaves[key]
                leaf.printInfo()


'''
def test_layerwiseDivision():
    print("result of sim_mat_1: ")
    sim_mat_1 = np.array([
        [1.0, 1.0, 1.0, 0.1, 0.1, 0.1],
        [1.0, 1.0, 1.0, 0.1, 0.1, 0.1],
        [1.0, 1.0, 1.0, 0.1, 0.1, 0.1],
        [0.1, 0.1, 0.1, 1.0, 0.95, 0.9],
        [0.1, 0.1, 0.1, 0.95, 1.0, 1.0],
        [0.1, 0.1, 0.1, 0.9, 1.0, 1.0],
    ])

    def clustering_lambda(data):
        reducted_data = RPReduction(data)
        reducted_data = SVDReduction(data, n_components=3)
        return KMeansClustering(reducted_data, 2)

    DN = DataNode(leaves_ind=list(range(0, 6)))
    DN.setCenter(sim_mat_1)
    DN.layerwiseDivision(sim_mat_1, clustering_lambda, 3,
                         n_jobs=2,
                         first_layer=True)
    # in layer 1, the centers should be: 0
    # in layer 2, the centers should be: 0 and 4
    # since they are closer to others in their own cluster
    DN.printInfo()

    print("result of sim_mat_2: ")
    sim_mat_2 = np.array([
        [1.0, 0.9, 1.0, 0.1, 0.1, 0.1],
        [0.9, 1.0, 0.93, 0.1, 0.1, 0.1],
        [1.0, 0.93, 1.0, 0.1, 0.1, 0.1],
        [0.1, 0.1, 0.1, 1.0, 0.95, 0.9],
        [0.1, 0.1, 0.1, 0.95, 1.0, 1.0],
        [0.1, 0.1, 0.1, 0.9, 1.0, 1.0],
    ])

    DN = DataNode(leaves_ind=list(range(0, 6)))
    DN.setCenter(sim_mat_2)
    DN.layerwiseDivision(sim_mat_2, clustering_lambda, 3,
                         n_jobs=2,
                         first_layer=True)
    # in layer 1, the centers should be: 4
    # in layer 2, the centers should be: 2 and 4
    # since they are closer to others in their own cluster
    DN.printInfo()


test_layerwiseDivision()
'''
