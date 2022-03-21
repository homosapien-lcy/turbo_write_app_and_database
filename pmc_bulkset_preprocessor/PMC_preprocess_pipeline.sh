# download commercial use list
wget https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_comm_use_file_list.csv
# generate PMCID list for all journals
python journalPaperPMCIDListGenerator.py ../PMC_commercial_paperset/unziped_papers/ ../PMC_commercial_paperset/journal_paper_pmcid_list
# collect PMCID for a subject
python subjectPMCIDCollector.py psychology_journal_list.csv ../PMC_commercial_paperset/journal_paper_pmcid_list/ psychology_PMCID_list
# collect related citing papers with degree 1
python subjectRelatedPaperListGenerator.py oa_comm_use_file_list.csv psychology_PMCID_list 1
# put all papers in 1 folder
python allPaperCollector.py nxml ../PMC_commercial_paperset/unziped_papers/ ../PMC_commercial_paperset/all_paper_collection
# collect psychology papers
python subjectPaperGatherer.py ../PMC_commercial_paperset/all_paper_collection/  ../PMC_commercial_paperset/psychology_paper_collection psychology_PMCID_list_degree_1_commercializable
