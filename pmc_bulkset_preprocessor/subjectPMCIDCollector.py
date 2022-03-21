'''
this script collect all PMCID for a subject given a journal list and PMCID folder
'''

import sys
from utils.IOUtils import *

journal_list_csv_fn = sys.argv[1]
journal_list = journalListFromCSV(journal_list_csv_fn)
journal_list = listStringConversion(
    journal_list, journalNameToSysFormat)

journal_pmcid_folder = sys.argv[2]
journal_pmcid_folder = folderNameGuard(journal_pmcid_folder)

subject_pmcid_fn = sys.argv[3]

pmcid_collection = []
for journal in journal_list:
    journal_pmcid_fn = journal_pmcid_folder + journal

    if os.path.exists(journal_pmcid_fn):
        PMCID_list = readListFromTxt(journal_pmcid_fn)
        pmcid_collection.extend(PMCID_list)

spf = open(subject_pmcid_fn, 'w')
spf.write('\n'.join(pmcid_collection))
spf.close()
