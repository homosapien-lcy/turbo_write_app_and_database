'''
collect all papers previously selected and list papers that are not local
'''
import sys
from utils.IOUtils import *
from utils.downloadUtils import *

# 300 is the max taken by the pmc server
# 240 with processing batch of 30 has the best performance (1680 papers takes 346s) for regex
# with json request 2400 paper only takes 73s
request_batch_size = 240

bulk_folder = sys.argv[1]
destination = sys.argv[2]

# guard folders
bulk_folder = folderNameGuard(bulk_folder)
destination = folderNameGuard(destination)

checkAndCreateFolder(destination)
# delete paper info file if existed
# because the savePaperInfo doesn't
# overwrite the content of file
checkAndDeletePaperInfo()

# load candidate list
subject_related_PMCID_fn = sys.argv[3]
subject_related_PMCID_list = readListFromTxt(subject_related_PMCID_fn)

list_in_bulk = []
list_to_download = []
num_paper_processed = 0
# process in batch
start = time.time()
for PMCID_batch in chunked(subject_related_PMCID_list, request_batch_size):
    # request info from API
    batch_num_cited = numCitedListRequest(PMCID_batch)
    batch_paper_info = getPaperInfoWithEsumm(PMCID_batch)
    for PMCID in batch_num_cited.keys():
        # construct filename in a list
        filename = 'PMC' + PMCID + '.nxml'
        filename = bulk_folder + filename

        # retrieve from data dictionary
        num_cited = batch_num_cited[PMCID]
        paper_info_json = batch_paper_info[PMCID]

        # get paper info
        paper_info = searchForAllInfoJSON(PMCID, num_cited, paper_info_json)

        # in case of exist on local disk
        if os.path.exists(filename):
            list_in_bulk.append(PMCID)
            # save paper info to local
            savePaperInfo(paper_info['journal_and_date'])
            # copy file to location
            copyToLoc(filename, destination)
        # if not, save for later download
        else:
            list_to_download.append(PMCID)

    num_paper_processed += request_batch_size
    print(num_paper_processed, 'have been processed')
    end = time.time()
    print('took', end - start, 'seconds')
    time.sleep(5)
    print('sleep for 5 seconds')

print(len(list_in_bulk), "papers already downloaded")
print(len(list_to_download),
      "papers to be downloaded, saving in:", "PMCID_to_download")

# write to disk
comm_PMCID_file = open('PMCID_to_download', 'w')
comm_PMCID_file.write('\n'.join(list_to_download))
comm_PMCID_file.close()
