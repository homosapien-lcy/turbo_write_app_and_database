import sys
import os
import pickle
import h5py
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

# save numpy array in format hdf5
# actually the same size if saving numpy array


def saveHDF5(np_arr, collection_name, filename):
    with h5py.File(filename, 'w') as f:
        f.create_dataset(collection_name, data=np_arr)

# load a collection from HDF5


def loadHDF5(collection_name, filename):
    with h5py.File(filename, 'r') as f:
        # copy, or the object will lost after close
        data = f[collection_name][:]

    return data

# remove file


def runRM(f):
    os.system("rm " + f)

# convert label array to dict from cluster to indeces


def labelArrToIndexDict(label_arr):
    index_dict = {}
    for (i, l) in enumerate(label_arr):
        if l not in index_dict.keys():
            index_dict[l] = [i]
        else:
            index_dict[l].append(i)

    return index_dict

# get elements of indexs from element_arr


def lookupIndex(element_arr, index_arr):
    selected_elements = [element_arr[index] for index in index_arr]
    return selected_elements

# convert number array to string


def numArrToString(num_arr):
    num_list = list(num_arr)
    num_str = ""
    for num in num_list:
        num_str += str(num) + " "

    return num_str

# write an array of string to file


def writeArrOfStringToFile(string_arr, f):
    f.write('\n'.join(string_arr) + '\n')

# extract cluster members with VP label and save to corresponding files


def extractClusterAndSave(data_list, VP_label_dict, cluster_file_dict):
    for clus_num in VP_label_dict.keys():
        clus_index_arr = VP_label_dict[clus_num]

        # extract writing items
        clus_data = lookupIndex(data_list, clus_index_arr)

        # convert to string if needed
        clus_data = [x if (type(x) is str) else str(x) for x in clus_data]

        # write to files
        writeArrOfStringToFile(
            clus_data, cluster_file_dict[clus_num])
