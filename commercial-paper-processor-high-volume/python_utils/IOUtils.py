import sys
import os
import pandas as pd

kb_300 = 1024 * 300
save_file = "processing_state"

# method that turn string word into boolean


def stringToBoolean(str):
    if str.lower() == "true":
        return True

    if str.lower() == "false":
        return False

    print("cannot recognize this boolean string, return default: False")
    return False

# method for obtain all file names in a folder


def getFilenamesFromFolder(folder_name):
    list_of_files = os.listdir(folder_name)
    list_of_files = [folder_name + fn for fn in list_of_files]
    return list_of_files


def readTxt(fn):
    f = open(fn, 'r')
    data = ""

    for line in f:
        data += line.strip() + " "

    f.close()

    return data

# write list of content into file


def writeFile(content, fn):
    out_file = open(fn, 'w')

    for i in range(0, len(content)):
        out_file.write(content[i] + ' \n')

    out_file.close()

# write list of BOW into file


def writeBOWs(BOWs, fn):
    out_file = open(fn, 'w')

    for i in range(0, len(BOWs)):
        out_file.write(' '.join(BOWs[i]) + ' \n')

    out_file.close()

# read database file for sentence database


def readDB(fn):
    in_file = open(fn, 'r')

    content = []
    for line in in_file:
        content.append(line.split())

    in_file.close()
    return content


# read file into list of content


def readFile(fn):
    in_file = open(fn, 'r')

    content = []
    for line in in_file:
        content.append(line.strip())

    in_file.close()
    return content


def filterBySize(list_of_files):
    return filter(lambda f: os.path.getsize(f) > kb_300, list_of_files)


def saveProcessingState(pdf_list):
    f = open(save_file, 'w')

    for pdf_filename in pdf_list:
        f.write(pdf_filename + ' \n')

    f.close()


def loadProcessingState():
    f = open(save_file, 'r')

    pdf_list = []
    for line in f:
        sl = line.split()
        pdf_list.append(sl[0])

    f.close()

    return pdf_list

# use pandas to save word embedding in table format


def saveWordEmbedding(words, embedding, filename):
    embedding_data_table = pd.DataFrame(data=embedding, index=words)
    embedding_data_table.to_pickle(filename)

# replace all '_' with ' ' to make it searchable


def savenameToSearchname(savename):
    return savename.strip().replace('_', ' ')

# read collection file of journal and year


def readCollectionFile(fn):
    f = open(fn, 'r')
    dictionary_colllection = []

    for line in f:
        sl = line.split()

        PMCID = sl[0]
        title = savenameToSearchname(sl[1])
        journal = savenameToSearchname(sl[2])
        journal_abbrev = savenameToSearchname(sl[3])
        year = sl[4]
        month = sl[5]
        day = sl[6]
        cited_times = sl[7]

        paper_info = {
            "PMCID": PMCID,
            "title": title,
            "journal": journal,
            "journal_abbrev": journal_abbrev,
            "year": year,
            "month": month,
            "day": day,
            "cited_times": cited_times
        }

        dictionary_colllection.append(paper_info)

    f.close()

    return dictionary_colllection

# read nxml texts


def readNxml(fn):
    with open(fn, 'r') as f:
        try:
            current_text = f.read()
        # if cannot read file, return empty string
        except:
            current_text = ""

    return current_text
