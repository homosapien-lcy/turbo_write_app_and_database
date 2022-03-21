import os
import json
from more_itertools import chunked


def fileAllIn(fn):
    with open(fn, 'r') as f:
        try:
            content = f.read()
        # if cannot read file, return empty string
        except:
            content = ""

    return content

# write dictionary to file for inspection


def writeDictToFile(dict):
    key_set = dict.keys()
    for k in key_set:
        f = open("category_" + str(k), 'w')
        f.write('\n'.join(dict[k]))

# method for obtain all file names in a folder


def getFilenamesFromFolder(folder_name):
    list_of_files = os.listdir(folder_name)
    list_of_files = [folder_name + fn for fn in list_of_files]
    return list_of_files

# read txt from all file in a folder


def importTxtData(folder):
    list_of_txt = getFilenamesFromFolder(folder)
    all_text = ""

    for txt_fn in list_of_txt:
        all_text += fileAllIn(txt_fn) + "\n"

    return all_text

# read txt from a list of


def importTxtFromList(txt_list):
    all_text = ""

    for txt_fn in txt_list:
        all_text += fileAllIn(txt_fn) + "\n"

    return all_text

# save collecion as json


def saveCollectionAsJson(collection_name, json_data):
    data_json_file = open(collection_name + ".json", 'w')
    json.dump(json_data, data_json_file)
    data_json_file.close()

# load json collection


def loadJsonData(json_fn):
    json_file = open(json_fn, 'r')
    json_data = json.load(json_file)
    json_file.close()
    return json_data
