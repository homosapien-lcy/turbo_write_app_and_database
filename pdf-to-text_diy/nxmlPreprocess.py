'''
process all nxml files from a folder for fasttext
'''
import sys
import time

from python_utils.preprocessing import *

folder_name = sys.argv[1]
output_fn = sys.argv[2]
mode = sys.argv[3]

if folder_name[-1] != '/':
    folder_name += '/'

if mode != 'ft' and mode != 'db':
    print('mode not recognized, must be either "ft" or "db" for fasttext or sentence database preprocessing')
    sys.exit(0)

list_of_nxml = getFilenamesFromFolder(folder_name)
print(len(list_of_nxml), 'in total')

start = time.time()

# process and join content
nxml_content_arr = readAndProcessNxmlFilesMP(list_of_nxml)
output_content = ' '.join(nxml_content_arr)

# for fasttext, remove .
if mode == 'ft':
    output_content = output_content.replace('.', '')

# output
fasttext_data_file = open(output_fn, 'w')
fasttext_data_file.write(output_content)
fasttext_data_file.close()

end = time.time()
print('processing takes a total of:', end - start, 'seconds')
