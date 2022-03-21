import os
import pandas as pd

save_file = "download_state"
paper_info_file = "paper_info_collection"


def checkAndCreateFolder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# save and load downloading status


def saveDownloadState(folder_to_save, PMC_ID_list):
    f = open(save_file, 'w')
    f.write(folder_to_save + '\n')

    for ID in PMC_ID_list:
        f.write(ID + ' \n')

    f.close()


def loadDownloadState():
    f = open(save_file, 'r')
    folder_to_save = f.readline().split()[0]

    PMC_ID_list = []
    for line in f:
        sl = line.split()
        ID = sl[0]
        PMC_ID_list.append(ID)

    f.close()

    return folder_to_save, PMC_ID_list

# function to save paper info to file


def savePaperInfo(journal_and_date):
    text_to_save = ' '.join(journal_and_date)
    if len(text_to_save.split()) != 8:
        print('WARNING: the length of information:')
        print(text_to_save)
        print('after splitting would be:')
        print(text_to_save.split())
        print('its length is not 8! Which can cause problems downstream such as elastic search, due to data mismatch')

    os.system("echo \"" + text_to_save + "\" >> " + paper_info_file)

# delete paper info when restart


def checkAndDeletePaperInfo():
    if os.path.exists(paper_info_file):
        os.system("rm \"" + paper_info_file + "\"")

# read the commercial use list into dictionary


def read_comm_file(fn):
    comm_file = open(fn, 'r')
    # remove line 1
    comm_file.readline()

    comm_paper_info = {}
    for line in comm_file:
        sl = line.strip().split(',')

        file_loc = sl[0]
        journal_name = sl[1]
        # remove PMC and only keep the numbers
        PMCID = sl[2][3:]
        modified_date = sl[3]
        PMID = sl[4]
        license_type = sl[5]

        comm_paper_info[PMCID] = {
            "file_loc": file_loc,
            "journal_name": journal_name,
            "PMCID": PMCID,
            "modified_date": modified_date,
            "PMID": PMID,
            "license_type": license_type
        }

    return comm_paper_info

# uncompress file and extract the nxml text


def extractNxmlFile(folder, PMCID):
    converted_PMCID = "PMC" + PMCID
    # extract nxml
    os.system("tar -xvf " + folder + converted_PMCID +
              # linux wildcard
              ".tar.gz --wildcards " + converted_PMCID + "/*.nxml")
    # mac wildcard
    # ".tar.gz '" + converted_PMCID + "/*.nxml'")

    # list all files
    nxml_files = os.listdir(converted_PMCID)
    for i, fn in enumerate(nxml_files):
        old_fn = converted_PMCID + "/" + fn
        new_fn = converted_PMCID + "/" + PMCID + "_" + str(i) + ".nxml"
        # change the file name to new one
        os.system("mv " + old_fn + " " + new_fn)

    # remove the tar.gz file to save space
    os.system("rm " + folder + converted_PMCID + ".tar.gz")

    # move all nxml to the data folder
    os.system("mv " + converted_PMCID + "/* " + folder)

    # remove the temporary dir
    os.system("rm -r " + converted_PMCID + "/")

# collect journal list from csv downloaded from scimago


def journalListFromCSV(journal_list_csv_fn):
    return pd.read_csv(journal_list_csv_fn, delimiter=';')['Title'].tolist()


def journalNameToSysFormat(journal_name):
    return journal_name.strip().replace(' ', '_')


def journalNameToDisplayFormat(journal_name):
    return journal_name.strip().replace('_', ' ')


def listStringConversion(string_list, conversion_operator):
    return map(conversion_operator, string_list)


def getContentsFromFolder(folder_name):
    list_of_contents = os.listdir(folder_name)
    list_of_contents = [folder_name + fn for fn in list_of_contents]
    return list_of_contents

# copy all files from journal to destination


def gatherFilesInFolderInList(folder, destination, journal_list):
    # safeguarding foldername
    if folder[-1] != '/':
        folder = folder + '/'

    checkAndCreateFolder(destination)

    for journal in journal_list:
        journal_folder_name = folder + journal
        print(journal_folder_name)
        # move folder content to destination
        if os.path.exists(journal_folder_name):
            copyToLoc(journal_folder_name + "/*", destination)

# copy to destination


def copyToLoc(f, destination):
    os.system("cp '" + f + "' '" + destination + "'")

# check whether a filename contains a tail


def hasTail(fn, tail):
    tail_len = len(tail)
    return fn[-tail_len:] == tail


def collectFilesRecursively(folder, tail):
    list_of_contents = getContentsFromFolder(folder)
    all_file_list = []
    for c in list_of_contents:
        if c[-4:] == '.zip' or c[-7:] == '.tar.gz':
            continue
        elif not hasTail(c, tail):
            c = folderNameGuard(c)
            all_file_list.extend(collectFilesRecursively(c, tail))
        else:
            all_file_list.append(c)

    return all_file_list


def folderNameGuard(folder_name):
    # safeguarding foldername
    if folder_name[-1] != '/':
        return folder_name + '/'

    return folder_name


def readListFromTxt(txt_file):
    l = []
    f = open(txt_file, 'r')
    for line in f:
        l.append(line.strip())

    return l


def PMCIDToFilename(PMCID):
    return 'PMC' + PMCID + '.nxml'
