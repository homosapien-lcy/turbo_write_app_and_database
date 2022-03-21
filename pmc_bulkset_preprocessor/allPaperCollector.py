# collecting all files into a folder
import sys
from utils.IOUtils import *

file_type = sys.argv[1]
bulk_folder = sys.argv[2]
destination = sys.argv[3]

bulk_folder = folderNameGuard(bulk_folder)
destination = folderNameGuard(destination)

checkAndCreateFolder(destination)

# safeguarding file type
if file_type[0] != '.':
    file_type = '.' + file_type

# collect files
all_file_list = collectFilesRecursively(bulk_folder, file_type)

print("In total", len(all_file_list), "files")

# copy to destination
for f in all_file_list:
    copyToLoc(f, destination)
