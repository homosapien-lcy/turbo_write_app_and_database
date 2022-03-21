import sys
import os
import time
import pickle
import pandas as pd

kb_300 = 1024 * 300
save_file = "processing_state"


def checkAndCreateFolder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

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


def readWholeFile(fn):
    f = open(fn, 'r')
    data = f.read()

    f.close()

    return data


def writeWholeFile(fn, content):
    f = open(fn, 'w')
    f.write(content)
    f.close()


def readTxt(fn):
    f = open(fn, 'r')
    data = ""

    for line in f:
        data += line.strip() + " "

    f.close()

    return data

# read nxml texts


def readNxml(fn):
    with open(fn, 'r') as f:
        try:
            current_text = f.read()
        # if cannot read file, return empty string
        except:
            current_text = ""

    return current_text

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


def loadProcessingState():
    f = open(save_file, 'r')

    pdf_list = []
    for line in f:
        sl = line.split()
        pdf_list.append(sl[0])

    return pdf_list

# use pandas to save word embedding in table format


def saveWordEmbedding(words, embedding, filename):
    embedding_data_table = pd.DataFrame(data=embedding, index=words)
    embedding_data_table.to_pickle(filename)

# save python object to pickle


def savePythonObject(py_obj, filename):
    f = open(filename, 'wb')
    pickle.dump(py_obj, f)
    f.close()

# load from pickle


def loadPythonObject(filename):
    f = open(filename, 'rb')
    py_obj = pickle.load(f)
    f.close()

    return py_obj

# load sentence database from file


def loadSentenceDB(filename):
    sentence_DB = readWholeFile(filename)
    sentence_DB = sentence_DB.split('. ')
    return sentence_DB


def uncompressFileToFolder(filename, folder):
    os.system("tar -C " + folder + " -zxvf " + filename)

# remove file


def runRM(f):
    os.system("rm " + f)

# remove all files in folder


def clearFolder(folder):
    # check and add tail
    if folder[-1] != '/':
        folder = folder + '/'

    runRM(folder + "*")


def removeFolder(folder):
    # check and add tail
    if folder[-1] != '/':
        folder = folder + '/'
    os.system("rm -r " + folder)
