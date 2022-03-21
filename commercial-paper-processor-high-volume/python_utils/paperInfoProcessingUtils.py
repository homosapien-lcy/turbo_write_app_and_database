from .IOUtils import *
from .extractionUtils import *
from .mpUtils import *

# add the lower cases to dictionary


def expandLowerCase(dict_to_expand):
    for key in dict_to_expand.keys():
        t_copy = dict_to_expand[key][:]
        for t in t_copy:
            dict_to_expand[key].append(t.lower())


Abstract_start_title_arr = ["Abstract", "Abstract:"]
Abstract_end_title_arr = ["Introduction", "Introduction:", "Introductions",  "Introduction:",
                          "Background", "Background:", "Backgrounds", "Backgrounds:"]

Intro_start_title_arr = ["Introduction", "Introduction:", "Introductions",  "Introduction:",
                         "Background", "Background:", "Backgrounds", "Backgrounds:"]
Intro_end_title_arr = ["Method", "Method:", "Methods",  "Methods:",
                       "Material and method", "Material and method:", "Material and methods", "Material and methods:",
                       "Materials and method", "Materials and method:", "Materials and methods", "Materials and methods:",
                       "Experiment", "Experiment:", "Experiments", "Experiments:", "Result", "Result:", "Results",  "Results:",
                       "Results and discussion", "Results and discussion:", "Results and discussions", "Results and discussions:"]

method_start_title_arr = ["Method", "Method:", "Methods",  "Methods:",
                          "Material and method", "Material and method:", "Material and methods", "Material and methods:",
                          "Materials and method", "Materials and method:", "Materials and methods", "Materials and methods:",
                          "Experiment", "Experiment:", "Experiments", "Experiments:"]
method_end_title_arr = ["Result", "Result:", "Results",  "Results:",
                        "Acknowledgment", "Acknowledgment:", "Acknowledgments", "Acknowledgments:",
                        "Results and discussion", "Results and discussion:", "Results and discussions", "Results and discussions:"]

Result_start_title_arr = ["Result", "Result:", "Results",  "Results:", "Results and discussion",
                          "Results and discussion:", "Results and discussions", "Results and discussions:"]
Result_end_title_arr = ["Discussion", "Discussion:", "Discussions",  "Discussions:",
                        "Conclusion", "Conclusion:", "Conclusions", "Conclusions:",
                        "Acknowledgment", "Acknowledgment:", "Acknowledgments", "Acknowledgments:",
                        "Summary", "Summary:", "Summaries", "Summaries:"]

Discussion_start_title_arr = ["Discussion",
                              "Discussion:", "Discussions",  "Discussions:"]
Discussion_end_title_arr = ["Conclusion", "Conclusion:", "Conclusions", "Conclusions:",
                            "Acknowledgment", "Acknowledgment:", "Acknowledgments", "Acknowledgments:",
                            "Summary", "Summary:", "Summaries", "Summaries:"]

start_dictionary = {"Abstract": Abstract_start_title_arr,
                    "Introduction": Intro_start_title_arr,
                    "Methods": method_start_title_arr,
                    "Results": Result_start_title_arr,
                    "Discussion": Discussion_start_title_arr}
end_dictionary = {"Abstract": Abstract_end_title_arr,
                  "Introduction": Intro_end_title_arr,
                  "Methods": method_end_title_arr,
                  "Results": Result_end_title_arr,
                  "Discussion": Discussion_end_title_arr}

# add lowercases
expandLowerCase(start_dictionary)
expandLowerCase(end_dictionary)


# flatten a nested list
# thanks, Alex Martelli


def flattenList(l):
    return [item for sublist in l for item in sublist]

# construct data from a paper info


def readAndExtractWithPaperInfo(i_and_paper_info):
    # unpack id and paper
    i, (folder, collection_name, num_group, paper_info) = i_and_paper_info

    PMCID = paper_info["PMCID"]
    # replace '&#x2019;' which is the hex of '
    title = paper_info["title"].replace("&#x2019", "'")
    # remove trans tag
    title = re.sub(html_trans_regex, '', title)
    journal = paper_info["journal"]
    year = paper_info["year"]
    cited_times = paper_info["cited_times"]

    nxml_text = loadNxmlFromPMCIDBulk(PMCID, folder)

    # check for None when file not exists
    if nxml_text is None:
        return None

    part_data_json_arr = []

    for section in start_dictionary.keys():
        start_title_arr = start_dictionary[section]
        end_title_arr = end_dictionary[section]

        section_text = extractSectionFromNxml(
            nxml_text, start_title_arr, end_title_arr)

        # only process none empty
        if len(section_text) > 0:
            # remove extra line breaks
            bag_of_paragraph = section_text.split('\n')
            bag_of_paragraph = filter(lambda s: len(s) > 0, bag_of_paragraph)
            section_text = ' '.join(bag_of_paragraph)
            # remove et al to prevent confusion from '.'
            section_text = subEtAl(section_text)

            # separate into sentences
            # change from '. ' to '.' to prevent some cases
            # of text sticking in nxml
            section_text = section_text.split(".")
            section_text = [s.strip() for s in section_text]
            section_text_group = elementNGroup(section_text, num_group)

            # loop through each sentence and make save data
            for j, sentence_group in enumerate(section_text_group):
                doc_id = i
                sent_id = j
                s = '. '.join(sentence_group)
                # remove extra space between words
                s = removeExtraSpace(s)

                # append if not empty
                if len(s) > 0:
                    # if not end with '.', add '.'
                    if s[-1] != '.':
                        s += '.'

                    part_data_json_arr.append({
                        '_index': collection_name,
                        'PMCID': PMCID,
                        'title': title,
                        'journal': journal,
                        'year': year,
                        'cited_times': cited_times,
                        'number_of_words': len(s.split()),
                        'doc_id': doc_id,
                        'sent_id': sent_id,
                        'section': section,
                        'content': s,
                        'num_group': num_group
                    })

    return part_data_json_arr


# single processor version of paper infor processor


def readAndExtractWithPaperInfoArrSingleP(paper_info_collection):
    data_json_arr = map(readAndExtractWithPaperInfo,
                        enumerate(paper_info_collection))

    # flatten the arr and return
    data_json_arr = flattenList(data_json_arr)
    return data_json_arr

# multi processor version of paper infor processor


def readAndExtractWithPaperInfoArrMultiP(paper_info_collection):
    # use parallelism to speed up, use 20 as chunk size
    # 4 processors are almost as fast as 8
    with eval(core_pool_4) as pool:
        data_json_arr = pool.map(
            readAndExtractWithPaperInfo, enumerate(paper_info_collection), 20)
        pool.close()
        pool.join()

    # flatten the arr and return
    data_json_arr = flattenList(data_json_arr)
    return data_json_arr

# construct data from a paper info
# compare to readAndExtractWithPaperInfo
# process single section with extra nxml processing
# for a similarity sentence database processing downstream


def readAndExtractWithPaperInfoForSimilarityDBProcessing(i_and_paper_info, processing_fun):
    # unpack id and paper
    i, (folder, collection_name, section, paper_info) = i_and_paper_info

    PMCID = paper_info["PMCID"]
    # replace '&#x2019;' which is the hex of '
    title = paper_info["title"].replace("&#x2019", "'")
    # remove trans tag
    title = re.sub(html_trans_regex, '', title)
    journal = paper_info["journal"]
    year = paper_info["year"]
    cited_times = paper_info["cited_times"]

    nxml_text = loadNxmlFromPMCIDBulk(PMCID, folder)

    start_title_arr = start_dictionary[section]
    end_title_arr = end_dictionary[section]

    section_text = extractAndProcessSectionFromNxml(
        nxml_text, start_title_arr, end_title_arr, processing_fun=processing_fun)

    if len(section_text) > 0:
        return section_text
    else:
        return ''

# single processor version of paper infor processor


def readAndExtractWithPaperInfoForSimilarityDBProcessingArrSingleP(paper_info_collection):
    data_arr = map(readAndExtractWithPaperInfoForSimilarityDBProcessing,
                   enumerate(paper_info_collection))

    # flatten the arr and return
    data_arr = flattenList(data_arr)
    return data_arr

# multi processor version of paper infor processor


def readAndExtractWithPaperInfoForSimilarityDBProcessingArrMultiP(paper_info_collection,
                                                                  processing_fun=processNxmlContent):
    # use parallelism to speed up, use 20 as chunk size
    # 4 processors are almost as fast as 8
    with eval(core_pool_4) as pool:
        data_arr = pool.map(
            partial(readAndExtractWithPaperInfoForSimilarityDBProcessing,
                    processing_fun=processing_fun),
            enumerate(paper_info_collection), 20)
        pool.close()
        pool.join()

    return data_arr
