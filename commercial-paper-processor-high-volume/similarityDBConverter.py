import sys
import time
import json
from os import listdir
from more_itertools import chunked

from python_utils.paperInfoProcessingUtils import *

paper_info_fn = sys.argv[1]
folder = sys.argv[2]
collection_name = sys.argv[3]
section = sys.argv[4]

if folder[-1] != "/":
    folder = folder + "/"

start = time.time()

paper_info_collection = readCollectionFile(paper_info_fn)

paper_info_collection_with_folder = [
    (folder, collection_name, section, p) for p in paper_info_collection]

processing_counter = 0

total_data_arr = []
for paper_info_batch in enumerate(paper_info_collection_with_folder):
    # read and extract from those batches
    batch_data_arr = readAndExtractWithPaperInfoForSimilarityDBProcessing(
        paper_info_batch, processNxmlContent)
    total_data_arr.append(batch_data_arr)

    processing_counter += 1
    end = time.time()
    print("Processing", processing_counter,
          "papers took:", end - start, "seconds")

data_file = open(collection_name + "_" + section, 'w')
data_file.write('\n'.join(total_data_arr))
data_file.close()
