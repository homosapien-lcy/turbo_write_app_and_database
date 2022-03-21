import re
from .mpUtils import *

date_info_regex = re.compile(r'(<pub-date(.*?)>(.*?)<\/pub-date>)')
year_regex = re.compile(r'(<year>(.*?)<\/year>)')
month_regex = re.compile(r'(<month>(.*?)<\/month>)')
day_regex = re.compile(r'(<day>(.*?)<\/day>)')
tag_regex = re.compile(r'<\/?(.*?)>')
journal_regex = re.compile(r'(<journal-title(.*?)>(.*?)</journal-title>)')
journal_abbrev_regex = re.compile(r'(<journal-id(.*?)>(.*?)</journal-id>)')
article_title_regex = re.compile(
    r'(<article-title(.*?)>(.*?)</article-title>)')

id_block_regex = re.compile(
    r'(<LinkSet>(.*?)</LinkSet>)')
paper_info_block_regex = re.compile(
    r'(<article(.*?)>(.*?)</article>)')
self_id_regex = re.compile(
    r'(<IdList(.*?)>(.*?)</IdList>)')
pmc_id_regex = re.compile(
    r'(<article-id pub-id-type="pmc">(.*?)</article-id>)')


def remove_tags(text):
    return re.sub(tag_regex, '', text).strip()


def cleanupHTMLForRegex(html_content):
    return ' '.join(html_content.split('\n'))

# a findall with guard for not found


def guardFindAll(regex, clean_html_content):
    found = re.findall(regex, clean_html_content)
    if len(found) == 0:
        return "N/A"

    return found[0][0]

# a findall with guard for not found for more than 1 match


def guardFindAllArr(regex, clean_html_content):
    found = re.findall(regex, clean_html_content)
    if len(found) == 0:
        return "N/A"

    return found

# extract the date info


def searchForDate(html_content):
    clean_html_content = cleanupHTMLForRegex(html_content)
    date_info = guardFindAll(date_info_regex, clean_html_content)

    year = guardFindAll(year_regex, date_info)
    month = guardFindAll(month_regex, date_info)
    day = guardFindAll(day_regex, date_info)

    return {
        'year': remove_tags(year),
        'month': remove_tags(month),
        'day': remove_tags(day)
    }


def removeNonAscii(text):
    return re.sub(r'[^\x00-\x7F]+', ' ', text)

# process journal name to be saveable


def processJournalName(journal_name):
    return removeNonAscii(journal_name).strip().replace(' ', '_')

# extract journal info


def searchForJournal(html_content):
    clean_html_content = cleanupHTMLForRegex(html_content)
    journal_abbrev = guardFindAll(journal_abbrev_regex, clean_html_content)
    journal = guardFindAll(journal_regex, clean_html_content)
    title = guardFindAll(article_title_regex, clean_html_content)

    return {
        'journal_abbrev': remove_tags(journal_abbrev),
        'journal': remove_tags(journal),
        'title': remove_tags(title)
    }

# search for info for a list of PMCID, single processor


def searchForAllInfoListRequestSP(html_content, batch_num_cited):
    clean_html_content = cleanupHTMLForRegex(html_content)
    paper_info_blocks = guardFindAllArr(
        paper_info_block_regex, clean_html_content)

    # only take the whole regex part
    paper_info_blocks = [p_i_b[0] for p_i_b in paper_info_blocks]

    paper_info_dict = {}
    for p_i_b in paper_info_blocks:
        PMCID = searchForPMCID(p_i_b)
        num_cited = batch_num_cited[PMCID]
        paper_info_dict[PMCID] = searchForAllInfo(PMCID, num_cited, p_i_b)

    return paper_info_dict

# helper function, returns PMCID and info for dictionary construction


def searchForAllInfoListRequestMPHelper(p_i_b, batch_num_cited):
    PMCID = searchForPMCID(p_i_b)
    num_cited = batch_num_cited[PMCID]
    return (PMCID, searchForAllInfo(PMCID, num_cited, p_i_b))

# search for info for a list of PMCID, multiprocessor
# return a dictionary of paper info indexed by PMCIDs


def searchForAllInfoListRequestMP(html_content, batch_num_cited):
    clean_html_content = cleanupHTMLForRegex(html_content)
    paper_info_blocks = guardFindAllArr(
        paper_info_block_regex, clean_html_content)

    # only take the whole regex part
    paper_info_blocks = [p_i_b[0] for p_i_b in paper_info_blocks]

    # use parallelism to speed up, use 25 as chunk size
    with eval(core_pool_4) as pool:
        pre_paper_info_dict = pool.map(partial(
            searchForAllInfoListRequestMPHelper, batch_num_cited=batch_num_cited),
            paper_info_blocks, 30)
        pool.close()
        pool.join()

    # construct dictionary
    paper_info_dict = {}
    for PMCID, paper_info in pre_paper_info_dict:
        paper_info_dict[PMCID] = paper_info

    return paper_info_dict


def searchForAllInfo(PMC_id, number_of_times_cited, html_content):
    date_info = searchForDate(html_content)
    journal_info = searchForJournal(html_content)

    # process name to remove space
    j = processJournalName(journal_info['journal'])
    ja = processJournalName(journal_info['journal_abbrev'])
    t = processJournalName(journal_info['title'])

    y = date_info['year']
    m = date_info['month']
    d = date_info['day']

    notc = str(number_of_times_cited)

    return {
        'PMC_id': PMC_id,
        'title': t,
        'journal': j,
        'journal_abbrev': ja,
        'year': y,
        'month': m,
        'day': d,
        'cited_times': notc,
        'journal_and_date': [PMC_id, t, j, ja,  y, m, d, notc]
    }

# return N/A when key not exist


def guardGetField(dict, key):
    if key not in dict:
        return 'N/A'
    else:
        field = dict[key]
        # edge case of an empty field
        if len(field.strip()) <= 0:
            field = "N/A"

        return field

# date info from date string


def getDateInfo(json_paper_info):
    # guard for empty pubdate
    if 'pubdate' not in json_paper_info:
        return {
            'year': 'N/A',
            'month': 'N/A',
            'day': 'N/A'
        }

    date_json_str = json_paper_info['pubdate']
    date = date_json_str.split()

    # return y m d according to the availability
    if len(date) <= 0:
        return {
            'year': 'N/A',
            'month': 'N/A',
            'day': 'N/A'
        }
    elif len(date) == 1:
        return {
            'year': date[0],
            'month': 'N/A',
            'day': 'N/A'
        }
    elif len(date) == 2:
        return {
            'year': date[0],
            'month':  date[1],
            'day': 'N/A'
        }
    elif len(date) >= 3:
        return {
            'year': date[0],
            'month':  date[1],
            'day': date[2]
        }

# get paper info from json


def searchForAllInfoJSON(PMC_id, number_of_times_cited, json_paper_info):
    date_info = getDateInfo(json_paper_info)

    # process name to remove space
    j = processJournalName(guardGetField(json_paper_info, 'fulljournalname'))
    ja = processJournalName(guardGetField(json_paper_info, 'source'))
    t = processJournalName(guardGetField(json_paper_info, 'title'))

    y = date_info['year']
    m = date_info['month']
    d = date_info['day']

    notc = str(number_of_times_cited)

    return {
        'PMC_id': PMC_id,
        'title': t,
        'journal': j,
        'journal_abbrev': ja,
        'year': y,
        'month': m,
        'day': d,
        'cited_times': notc,
        'journal_and_date': [PMC_id, t, j, ja,  y, m, d, notc]
    }

# get id of itself from the cited html


def selfID(html_content):
    self_id_block = guardFindAllArr(
        self_id_regex, html_content)[0][0]
    return remove_tags(self_id_block)

# find the pmc id from the html


def searchForPMCID(html_content):
    PMCID_blocks = guardFindAll(pmc_id_regex, html_content)
    return remove_tags(PMCID_blocks)
