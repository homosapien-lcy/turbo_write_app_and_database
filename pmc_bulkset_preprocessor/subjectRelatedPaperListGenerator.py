import sys
from utils.IOUtils import *
from utils.downloadUtils import *

comm_list_fn = sys.argv[1]
comm_paper_info = read_comm_file(comm_list_fn)

PMCID_list_fn = sys.argv[2]
# what degree of papers need to be related
paper_related_degree = int(sys.argv[3])

PMCID_list = readListFromTxt(PMCID_list_fn)

total_related_PMCID_list = []
related_PMCID = collectCitationForRounds(
    PMCID_list, paper_related_degree, batch_size=100)

# commercially available by intersecting with comm list
comm_PMCID = set(related_PMCID) & set(comm_paper_info.keys())
comm_PMCID = list(comm_PMCID)
print('total commercializable papers:', len(comm_PMCID))

# write to disk
comm_PMCID_file = open(PMCID_list_fn + '_degree_' +
                       str(paper_related_degree) + '_commercializable', 'w')
comm_PMCID_file.write('\n'.join(comm_PMCID))
comm_PMCID_file.close()
