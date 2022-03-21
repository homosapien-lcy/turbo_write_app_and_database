from python_utils.preprocessing import *

data_folder = sys.argv[1]
output_fn = sys.argv[2]
mode = sys.argv[3].lower()

# add '/ if not added
if data_folder[-1] != '/':
    data_folder += '/'

if mode != 'ft' and mode != 'db' and mode != 'svo' and mode != 'for_display':
    print('mode not recognized, must be "ft", "db", "svo" or "for_display" for fasttext or sentence database preprocessing')
    sys.exit(0)

# open for writing
out_file = open(output_fn, 'w')

# get list fo all pkl files
list_of_collection_pkl = getFilenamesFromFolder(
    data_folder)

for fn in list_of_collection_pkl:
    start = time.time()

    sub_title_abstracts = extractTitleAbstractHelper(fn, mode)

    print("in total", len(sub_title_abstracts), "sentences")

    output_content = processContentForWriting(sub_title_abstracts, mode)
    # write constantly to save memory
    out_file.write(output_content)

    end = time.time()
    print("this takes:", end - start, "seconds")

# close file after writing
out_file.close()
