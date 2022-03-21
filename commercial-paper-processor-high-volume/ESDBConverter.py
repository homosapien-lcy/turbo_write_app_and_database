import sys
import time
import json
from os import listdir
from more_itertools import chunked

from python_utils.paperInfoProcessingUtils import *

paper_info_fn = sys.argv[1]
# paper collection folder
folder = sys.argv[2]
collection_name = sys.argv[3]
# how many sentence in 1 search group
num_group = int(sys.argv[4])

if folder[-1] != "/":
    folder = folder + "/"

start = time.time()

paper_info_collection = readCollectionFile(paper_info_fn)

paper_info_collection_with_folder = [
    (folder, collection_name, num_group, p) for p in paper_info_collection]

processing_counter = 0
# open for writing
data_json_file = open(collection_name + "_db_num_group_" +
                      str(num_group) + ".json", 'w')
for paper_info_batch in enumerate(paper_info_collection_with_folder):
    # read and extract from those batches
    batch_data_json_arr = readAndExtractWithPaperInfo(
        paper_info_batch)

    if batch_data_json_arr is not None and len(batch_data_json_arr) > 0:
        json.dump(batch_data_json_arr, data_json_file)
        # write a line to seperate each json
        data_json_file.write('\n')

data_json_file.close()
