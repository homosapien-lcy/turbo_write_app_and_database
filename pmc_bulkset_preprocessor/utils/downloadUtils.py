import os
import sys
import re
import time
import json
import wget
from more_itertools import chunked

import requests
from numpy.random import choice
from numpy.random import uniform
from urllib.request import Request, urlopen
import urllib.error
import http.client

from .textProcessingUtils import *

firefox_headers = {'User-Agent': 'Mozilla/5.0'}
chrome_headers = {'User-Agent': 'Chrome/39.0.2171.95'}

cites_keyval = "pmc_pmc_cites"
citedby_keyval = "pmc_pmc_citedby"

PMC_citation_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
PMC_fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PMC_summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

ftp_prefix = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/"

# open the link with a header


def wrappedOpen(url, headers=firefox_headers):
    # use a header to prevent blocking by service
    req = Request(url, headers=headers)
    # try open the page
    try:
        page = urlopen(req)
    # if fail, print error and return None for downstream
    # processing
    except urllib.error.HTTPError as e:
        print("open failed by code: ", e.code)
        return None
    except urllib.error.URLError as e:
        print("open failed by url error")
        return None

    return page

# get request with a header


def wrappedGet(url, params={}, headers=firefox_headers):
    try:
        req = requests.get(url, params=params, headers=headers)
        return req
    # if cannot open, try again
    except requests.exceptions.ConnectionError as err:
        print("run into: ", err)
        print("try again")
        return wrappedGet(url, params=params, headers=headers)


# request a list of citations and return
# paper_id can be an ID or an ID list


def requestCitations(paper_id, citation_option):
    citations = wrappedGet(url=PMC_citation_url, params={"dbfrom": "pubmed",
                                                         "linkname": citation_option,
                                                         "id": paper_id})

    citations = citations.content.decode("utf-8")
    return citations

# request the info of the paper


def requestPaperInfo(paper_id):
    paper_info = wrappedGet(url=PMC_fetch_url, params={"db": "pmc",
                                                       "id": paper_id})

    paper_info = paper_info.content.decode("utf-8")
    return paper_info

# request the info of the paper


def requestPaperInfoEsumm(paper_id, retmode):
    # the esumm request has a bug that it uses ',' other than '&id='
    # like other requests, need to process by customize code
    id_request_string = ','.join(paper_id)
    paper_info = wrappedGet(url=PMC_summary_url, params={"db": "pmc",
                                                         "id": id_request_string,
                                                         "retmode": retmode})
    paper_info = json.loads(paper_info.content)['result']

    return paper_info

# open content and convert to utf-8
# also return the redirected url


def getAddressAndContent(url):
    link = wrappedGet(url)

    # if successful, get the information
    if link.status_code == 200:
        redirected_link = link.url
        content = link.content.decode("utf-8")
    # else, pass None for next layer to handle
    else:
        print("retrieve content failed by code: ", link.status_code)
        redirected_link = None
        content = None

    return redirected_link, content

# find all PDF links and dois from a page's url


def findPDFLinks(url):
    true_url, content = getAddressAndContent(url)
    # if fail to open, return empty to end retrieval
    if true_url == None:
        PDF_links_list = []
    else:
        prefix = findPrefixLink(true_url)
        PDF_links_list = getPDFLinksInPage(content, prefix, true_url)

    return PDF_links_list

# find all PDF links and dois from a list of url


def findPDFLinksArr(url_arr):
    PDF_links_list = []

    for url in url_arr:
        sub_PDF_links_list = findPDFLinks(url)
        PDF_links_list.extend(sub_PDF_links_list)

    return PDF_links_list


# gets the papers that cites or cited by this paper


def getID(paper_id, citation_option):
    citation_xml = requestCitations(paper_id, citation_option)
    citation_xml = cleanupHTMLForRegex(citation_xml)
    citation_IDs = re.findall(r'<Id>(.*?)</Id>', citation_xml)
    return citation_IDs


def getCitesID(paper_id):
    return getID(paper_id, citation_option=cites_keyval)


def getCitedbyID(paper_id):
    return getID(paper_id, citation_option=citedby_keyval)


def numCitedFromHtml(citation_xml):
    return len(re.findall(r'<Id>(.*?)</Id>', citation_xml))


# remove the duplicates


def uniquify(arr):
    return list(set(arr))

# collect citations recursively until the citations reach
# or more than the target_num


def collectCitationRecursivelyHelper(paper_id):
    IDs_collected = []

    citedby = getCitedbyID(paper_id)
    cites = getCitesID(paper_id)

    IDs_collected.extend(citedby)
    IDs_collected.extend(cites)

    print(paper_id, "is cited by", citedby,
          "is citing", cites)

    return uniquify(IDs_collected)

# collect for a certain number of rounds


def collectCitationForRounds(paper_id_list, num_rounds, batch_size=10):
    total_collection = paper_id_list
    for i in range(0, num_rounds):
        current_round_collected = []
        # collect in batch to save request time
        for paper_id_batch in chunked(total_collection, batch_size):
            current_round_collected.extend(
                collectCitationRecursivelyHelper(paper_id_batch))

        # handle edge case, if num of id too small to start a loop
        # collect from all
        if len(total_collection) < batch_size:
            current_round_collected = collectCitationRecursivelyHelper(
                total_collection)

        total_collection = uniquify(current_round_collected)

        print("Finish processing round:", i)

    return uniquify(total_collection)


def collectCitationRecursively(paper_id, target_num, batch_size=10):
    # start by collecting ids related to the paper_id
    total_IDs_collected = collectCitationRecursivelyHelper(paper_id)

    # while number of ids collected is less than the target values
    # collect recursively
    while len(total_IDs_collected) < target_num:
        current_round_collected = []

        for ID_batch in chunked(total_IDs_collected, batch_size):
            current_round_collected.extend(
                collectCitationRecursivelyHelper(ID_batch))

        # handle edge case, if num of id too small to start a loop
        # collect from all
        if len(total_IDs_collected) < batch_size:
            current_round_collected = collectCitationRecursivelyHelper(
                total_IDs_collected)

        # remove duplicates
        current_round_collected = uniquify(current_round_collected)

        # test whether all the newly collected has already been
        # collected previously, if such is the case, break to
        # prevent infinite loop
        if set(current_round_collected).issubset(set(total_IDs_collected)):
            print("cannot find more related citations!")
            print("terminated with " + str(len(total_IDs_collected)) + " citations")
            break

        # add to the whole collection
        total_IDs_collected.extend(current_round_collected)
        # remove duplicates
        total_IDs_collected = uniquify(total_IDs_collected)

    return total_IDs_collected


# convert PMC id into link to paper


def PMCIDToLink(pmc_id):
    return "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC" + pmc_id

# convert all PMCIDs in the list


def PMCIDToLinkArr(pmc_id_arr):
    return [PMCIDToLink(pmc_id) for pmc_id in pmc_id_arr]

# download files (pdf)


def downloadFile(url, filename):
    # if file already downloaded
    # return
    '''
    if os.path.exists(filename):
        print("file already downloaded")
        return
    '''

    web_file = wrappedOpen(url)
    # if successfully open, save file
    if web_file != None:
        # shorten the name if the filename is too long
        if len(filename) > 60:
            filename = "data/" + filename[-50:]

        local_file = open(filename, 'wb')

        try:
            local_file.write(web_file.read())
        except http.client.IncompleteRead as e:
            print("incompleteRead error!")
            print("only get some partial data as shown below: ")
            print(e.partial)

            # write the partially downloaded content
            local_file.write(e.partial)

            print("close files and restarting program...")
            web_file.close()
            local_file.close()

            # remove file to avoid confusion
            os.remove(filename)

            # restart program
            os.execv(sys.executable, ['python'] + sys.argv)

        web_file.close()
        local_file.close()
    else:
        print("download failed")

# download a list of PDFs


def downloadPDFs(PMC_ID, PDF_url_list, folder_name):
    for i, url in enumerate(PDF_url_list):
        print("start downloading: ", url)
        # use pmc id as download name for better data management
        filename = folder_name + PMC_ID + "_" + str(i) + ".pdf"
        print("save as: ", filename)
        downloadFile(url, filename)

        kb_100 = 1024 * 100
        # if download file < 100kb, indicating fail to redirect
        # use webdriver to get real address and redownload
        if os.path.exists(filename):
            if os.path.getsize(filename) < kb_100:
                # generate operator for downloading
                download_op = downloadOperatorGen(downloadFile, filename)
                _ = browserAction(url, download_op)

        print("finish downloading: ", url)


def downloadWithPMCID(PMC_ID, folder_to_save):
    link_to_paper = PMCIDToLink(PMC_ID)
    pdf_links = findPDFLinks(link_to_paper)
    downloadPDFs(PMC_ID, pdf_links, folder_to_save)

# generate a time


def genTime(options, probs):
    return choice(a=options, p=probs) * uniform(0.7, 1.3)

# generate an array of time


def genTimeArr(size, options, probs):
    return [genTime(options, probs) for i in range(0, size)]

# get number of time a paper is cited from a single PMCID


def numCitedPMCID(paper_id):
    return len(getCitedbyID(PMC_id))

# get number of time cited for array of paper


def numCitedListRequest(paper_id_list):
    citation_xml = requestCitations(paper_id_list, citedby_keyval)
    clean_html_content = cleanupHTMLForRegex(citation_xml)
    id_blocks = guardFindAllArr(
        id_block_regex, clean_html_content)

    # only take the whole regex part
    id_blocks = [i_b[0] for i_b in id_blocks]

    cited_by_info_dict = {}
    for i_b in id_blocks:
        self_id = selfID(i_b)
        num_cited = numCitedFromHtml(i_b)
        cited_by_info_dict[self_id] = num_cited

    return cited_by_info_dict


# get the info of paper to download for documentation


def getDownloadPaperInfo(PMC_id):
    paper_info_html = requestPaperInfo(PMC_id)
    number_of_times_cited = numCitedPMCID(PMC_id)
    return searchForAllInfo(PMC_id, number_of_times_cited, paper_info_html)

# download file by calling wget


def wgetDownload(url, folder):
    #os.system("wget " + url + " -P " + folder)
    try:
        wget.download(url, folder)
    except Exception as e:
        print("ftp download fail, reconnecting in 10 minutes")
        # if fail, sleep and try again
        time.sleep(600)
        wgetDownload(url, folder)

# ftp download


def ftpLinkDownload(ftp_link, folder):
    wgetDownload(ftp_prefix + ftp_link, folder)

# getting paper info using esummary


def getPaperInfoWithEsumm(batch_PMCID_list):
    batch_journal_info = requestPaperInfoEsumm(batch_PMCID_list, 'json')
    return batch_journal_info
