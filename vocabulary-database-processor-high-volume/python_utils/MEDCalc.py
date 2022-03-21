import numpy as np
from .preprocessing import *
from Levenshtein import distance as MED_distance

# calculate MED and normalize with string length


def normalizedMED(s1, s2):
    distance = MED_distance(removeSpace(s1), removeSpace(s2))
    norm_factor = max(len(s1), len(s2))
    return float(distance) / float(norm_factor)


'''
calculating the minimum editing distance matrix
need to split to remove all spaces, or will be too slow
and send null back to the server
'''


def MEDMatCalc(s_list):
    MED_mat = [[normalizedMED(s_list[i], s_list[j]) for j in range(
        0, len(s_list))] for i in range(0, len(s_list))]
    return np.array(MED_mat)
