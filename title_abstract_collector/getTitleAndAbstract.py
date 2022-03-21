import sys
from utils.IOUtils import *
from utils.downloadUtils import *

# maximum query size = 200
processing_batch_size = 200
size_each_save_file = 100000
folder_to_save = "data/"

# if save file already exist, load from there
if os.path.exists(save_file):
    file_to_save, PMIDs_to_download = loadDownloadState()
    print("Loading previous downloading status: ")
    print("file to save: ", file_to_save)
else:
    start_PMID = int(sys.argv[1])
    end_PMID = int(sys.argv[2])
    file_to_save = sys.argv[3]
    PMIDs_to_download = list(range(start_PMID, end_PMID))
    PMIDs_to_download = [str(ID) for ID in PMIDs_to_download]

    saveDownloadState(file_to_save, PMIDs_to_download)

# check and create the folder for file saving
checkAndCreateFolder(folder_to_save)

cur_save_start_ID = int(PMIDs_to_download[0])
cur_ID = cur_save_start_ID
cur_save_end_ID = cur_save_start_ID + size_each_save_file

info_collection = []
cur_save_start_time = time.time()
while len(PMIDs_to_download) > 0:
    start = time.time()
    batch_PMID_list = popBatchFromList(
        PMIDs_to_download, processing_batch_size)
    batch_info_arr = collectBatchPubmedPaperInfoSP(batch_PMID_list)
    info_collection.extend(batch_info_arr)
    end = time.time()
    print("batch from", batch_PMID_list[0], "to",
          batch_PMID_list[-1], "took", end-start, "seconds")

    cur_ID += processing_batch_size
    # when accumulate enough data
    if cur_ID >= cur_save_end_ID:
        print("saving data " + str(cur_save_start_ID) + "-" + str(cur_ID))
        # save
        savePythonObject(info_collection, folder_to_save + file_to_save + "_" +
                         str(cur_save_start_ID) + "-" + str(cur_ID) + ".pkl")
        # clear collection
        info_collection = []

        # restart counting
        cur_save_start_ID = cur_save_end_ID
        cur_save_end_ID = cur_save_start_ID + size_each_save_file

        # saving download state as well
        # save here to prevent data not save when interrupting between save files
        saveDownloadState(file_to_save, PMIDs_to_download)
        cur_save_end_time = time.time()
        print("this save file takes:", cur_save_end_time - cur_save_start_time)
        # sleep at end of each cycle
        time.sleep(10)

    time.sleep(5)

# check for emptiness
if len(info_collection):
    # save last round
    savePythonObject(info_collection, folder_to_save + file_to_save + "_" +
                     str(cur_save_start_ID) + "-" + str(cur_ID) + ".pkl")

# remove the state file to complete download
os.remove(save_file)
