# generate list of PMCID for all journals in the bulk folder
import sys
from utils.IOUtils import *
from utils.dictionaryUtils import *

bulk_folder = sys.argv[1]
destination = sys.argv[2]

bulk_folder = folderNameGuard(bulk_folder)
destination = folderNameGuard(destination)

checkAndCreateFolder(destination)

# collect files
all_file_list = collectFilesRecursively(bulk_folder, '.nxml')

# collect PMCID
journal_list_dict = {}
for f in all_file_list:
    sf = f.split('/')
    paper = sf[-1].split('.')[0][3:]
    journal = sf[-2]

    checkAndAdd(journal_list_dict, journal, paper)

# generate PMCID list in a folder
for k in journal_list_dict.keys():
    paper_list = journal_list_dict[k]

    # write to file
    f = open(destination + k, 'w')
    f.write('\n'.join(paper_list))
    f.close()
