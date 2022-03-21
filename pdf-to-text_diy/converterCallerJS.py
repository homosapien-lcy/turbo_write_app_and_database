import sys
from Naked.toolshed.shell import execute_js, muterun_js
import time

from python_utils.IOUtils import *

if os.path.exists(save_file):
    pdf_list = loadProcessingState()
    print("loading previous processing state: ")
else:
    folder = sys.argv[1]

    # safeguarding foldername
    if folder[-1] != '/':
        folder = folder + '/'

    pdf_list = os.listdir(folder)
    pdf_list = [folder + pdf for pdf in pdf_list]
    pdf_list = filterBySize(pdf_list)
    pdf_list = list(pdf_list)

    saveProcessingState(pdf_list)

print("list of pdfs to process: ")
print(pdf_list)
print("in total: ")
print(len(pdf_list))

cmd_head = "converter.js "

while len(pdf_list) != 0:
    pdf = pdf_list.pop(0)

    cmd = cmd_head + pdf
    output = execute_js(cmd)
    print(output)

    # save the status after each process
    saveProcessingState(pdf_list)

# remove the state file to complete processing
os.remove(save_file)
