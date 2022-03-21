import sys

from python_utils.preprocessing import *
from python_utils.numericalAnalysisUtils import *
from python_utils.embeddingUtils import *

file_name = sys.argv[1]

# read embedding from saved pickle file
embedding_data = pd.read_pickle(file_name)
print("read embedding:", embedding_data)

# do clustering of word to check embedding quality
word_clusters = AGClustering(
    embedding_data, n_clusters=20, metric='cosine', linkage_criteria='average')

#embedding['cluster_ID'] = word_clusters.labels_

embedding = Embedding(embedding_data)
print(embedding.checkSimilarities("chromosom"))
