import os
import re

from .textProcessingUtils import *


def loadNxmlFromPMCID(PMCID, folder):
    all_text = ""
    file_id = 0
    while True:
        filename = folder + PMCID + "_" + str(file_id) + ".nxml"
        # if not exist, break
        if not os.path.exists(filename):
            break

        with open(filename, 'r') as f:
            try:
                current_text = f.read()
            # if cannot read file, return empty string
            except:
                current_text = ""

        all_text += current_text + " \n"

        file_id += 1

    return all_text

# load function for PMC paper file downloaded in bulk


def loadNxmlFromPMCIDBulk(PMCID, folder):
    filename = folder + "PMC" + PMCID + ".nxml"
    # if not exist, break
    if not os.path.exists(filename):
        print('file', filename, ' not found')
        return

    with open(filename, 'r') as f:
        try:
            current_text = f.read()
        # if cannot read file, return empty string
        except:
            current_text = ""

    return current_text

# convert title to regex
# but it turns out to have no effect


def titleToRegex(title):
    return title.replace(' ', '\s')

# extract section between start and end titles, with text input


def extractSectionFromText(input_text, start_title_arr, end_title_arr):
    section_text = ""
    start_collecting = False
    # a boolean that test whether the section
    # extracted is a real method section
    section_exist_in_text = False

    input_text_by_line = input_text.split('\n')
    for line in input_text_by_line:
        line = line.strip()

        # if the tail of the text match end title, end the process
        if hasTailIn(line, end_title_arr):
            section_exist_in_text = True
            break

        # if the collecting has start
        if start_collecting:
            section_text += line + "\n"

        # if the tail of the text match start title, start
        if hasTailIn(line, start_title_arr):
            start_collecting = True

    section_text = section_text.strip()

    # if the section extracted is not a real
    # section, return empty
    if not section_exist_in_text:
        section_text = ""

    return section_text

# extract section between start and end titles, with text input


def extractSectionFromNxml(input_nxml, start_title_arr, end_title_arr):
    total_section_text = ""

    # indicator whether it is found
    section_found = False
    for start in start_title_arr:
        # break the loop if sth is already found
        # to prevent redundant results in database
        if section_found:
            break

        for end in end_title_arr:
            # handle type 1 section title: <title>section_name</title>
            start_string = "<title>" + start + "<\/title>"
            end_string = "<title>" + end + "<\/title>"

            section_regex = re.compile(
                r'{start_string}(.*?){end_string}'.format(start_string=start_string, end_string=end_string))

            section_text = re.findall(section_regex, input_nxml)

            # if found, add to array
            if len(section_text) > 0:
                # the main section text is usually the last found
                total_section_text += section_text[-1]
                # set indicator to true and return
                section_found = True
                break

            # handle type 2 section title: <section_name>...</section_name>
            section_regex = re.compile(
                r'<{start_string}>(.*?)<\/{start_string}>'.format(start_string=start_string))

            section_text = re.findall(section_regex, input_nxml)

            # if found, add to array
            if len(section_text) > 0:
                # the main section text is usually the last found
                total_section_text += section_text[-1]
                # set indicator to true and return
                section_found = True
                break

    # comment out, since it will cause some words not in idf vocabulary appearing
    # which may be cause by "removeHtmltags" since it removes also the tag that marks
    # the list of references and cause the words in it to remain in the data
    '''
    # remove paragraph or section or title start symbol
    total_section_text = re.sub(start_regex, ' ', total_section_text)
    # add line break at the end of paragraph or section or title
    total_section_text = re.sub(end_regex, '\n', total_section_text)

    # remove reference tags
    total_section_text = removeInLineReferenceTags(total_section_text)
    # remove all html tags
    total_section_text = removeHtmltags(total_section_text)
    # replace dashes
    total_section_text = subDash(total_section_text)
    # remove html transformation
    total_section_text = removeHtmlTrans(total_section_text)
    '''

    return total_section_text

# lightly process content, for POS tagging and SVO


def lightlyProcessContent(nxml_input):
    # process
    nxml_content = removeLineBreaks(nxml_input)
    nxml_content = removeReferences(nxml_content)
    nxml_content = removeHtmltags(nxml_content)
    nxml_content = decodeUrlInfo(nxml_content)
    nxml_content = subDash(nxml_content)
    nxml_content = removeHtmlTrans(nxml_content)
    # change all '.' to '. '
    '''
    fix period already contain remove extra space
    do this before wordwise processing because: if a period is not fix
    there can be situations like: ... some extra space.3 boxes... where
    3 is not replace but it should be
    '''
    nxml_content = fixPeriod(nxml_content)

    return nxml_content

# process nxml content


def processNxmlContent(nxml_input):
    # process
    nxml_content = removeLineBreaks(nxml_input)
    nxml_content = removeReferences(nxml_content)
    nxml_content = removeHtmltags(nxml_content)
    nxml_content = decodeUrlInfo(nxml_content)
    nxml_content = subDash(nxml_content)
    nxml_content = removeHtmlTrans(nxml_content)
    nxml_content = subEtAl(nxml_content)
    nxml_content = subPunct(nxml_content, punct_list_without_period)
    # change all '.' to '. '
    '''
    fix period already contain remove extra space
    do this before wordwise processing because: if a period is not fix
    there can be situations like: ... some extra space.3 boxes... where
    3 is not replace but it should be
    '''
    nxml_content = fixPeriod(nxml_content)
    nxml_content = nxml_content.lower()
    nxml_content = wordWiseProcessing(
        nxml_content, [filterSingleChar, replaceFigureArrHelper, replaceNumericalArrHelper])
    # since D_A_T_A and F_I_G_U_R_E are caps, need to convert to lower again
    nxml_content = nxml_content.lower()

    return nxml_content

# extract and process


def extractAndProcessSectionFromNxml(input_nxml, start_title_arr, end_title_arr, processing_fun):
    total_section_text = extractSectionFromNxml(
        input_nxml, start_title_arr, end_title_arr)
    processed_total_section_text = processing_fun(total_section_text)
    return processed_total_section_text
