# generate ES Database
python ESDBConverter.py ../pmc_bulkset_preprocessor/paper_info_collection ../PMC_commercial_paperset/psychology_paper_collection/ psychology 3
# generate similarity DB data
python similarityDBConverter.py ../pmc_bulkset_preprocessor/paper_info_collection ../PMC_commercial_paperset/psychology_paper_collection/ psychology Abstract
python similarityDBConverter.py ../pmc_bulkset_preprocessor/paper_info_collection ../PMC_commercial_paperset/psychology_paper_collection/ psychology Introduction
python similarityDBConverter.py ../pmc_bulkset_preprocessor/paper_info_collection ../PMC_commercial_paperset/psychology_paper_collection/ psychology Methods
python similarityDBConverter.py ../pmc_bulkset_preprocessor/paper_info_collection ../PMC_commercial_paperset/psychology_paper_collection/ psychology Results
python similarityDBConverter.py ../pmc_bulkset_preprocessor/paper_info_collection ../PMC_commercial_paperset/psychology_paper_collection/ psychology Discussion
