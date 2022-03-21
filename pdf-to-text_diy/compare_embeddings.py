import sys
import pandas as pd

e1_fn = sys.argv[1]
e2_fn = sys.argv[2]

embedding_1 = pd.read_pickle(e1_fn)
embedding_2 = pd.read_pickle(e2_fn)

print(embedding_1 - embedding_2)
