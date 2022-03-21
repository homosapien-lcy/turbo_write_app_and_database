from python_utils.processorUtils import *

tag_regex = re.compile(r"<(.*?)>")

TOP_CUT_UNI = 50000
TOP_CUT_BI = 10000
TOP_CUT_TRI = 7000

# the factors that use to precut and save memory
pre_cut_factor = 5

pre_TOP_CUT_UNI = TOP_CUT_UNI * pre_cut_factor
pre_TOP_CUT_BI = TOP_CUT_BI * pre_cut_factor
pre_TOP_CUT_TRI = TOP_CUT_TRI * pre_cut_factor

digit_percent_cut = 0.1
punct_percent_cut = 0.05
length_cut = 20
feature_num = 100

number_of_PC = 20
number_of_cluster = 20

processing_batch_size = 5000

interpolation_model = {
    'unigram': 1,
    'bigram': 15,
    'trigram': 100
}

folder = sys.argv[1]
collection_name = sys.argv[2]

# safeguarding foldername
if folder[-1] != '/':
    folder = folder + '/'

start = time.time()

# get all file names in folder
all_nxml_filenames = getFilenamesFromFolder(folder)

# initialize empty word table
total_word_table = {
    'unigram': Counter([]),
    'bigram': Counter([]),
    'trigram': Counter([])
}
for nxml_filename_batch in chunked(all_nxml_filenames, processing_batch_size):
    batch_text_data = importTxtFromList(nxml_filename_batch)

    # remove unicode characters
    processed_test_data = bytes(batch_text_data, 'utf-8').decode('utf-8',
                                                                 'ignore').encode('ascii', errors='ignore').decode()
    # remove null bytes
    processed_test_data = removeNull(processed_test_data)
    # remove line breaks
    processed_test_data = ' '.join(processed_test_data.split('\n'))
    # replace all tags with space
    processed_test_data = re.sub(tag_regex, ' ', processed_test_data)

    # generate word table
    current_word_table = generateWordTable(processed_test_data)

    # add to total word table
    total_word_table = mergeDictionaryCounter(
        [total_word_table, current_word_table])

    # preselect to save memory
    total_word_table = keepTopInDictionary(
        total_word_table,
        {
            'unigram': pre_TOP_CUT_UNI,
            'bigram': pre_TOP_CUT_BI,
            'trigram': pre_TOP_CUT_TRI
        })

# keep the top grams
total_selected_gram_table = keepTopInDictionary(
    total_word_table,
    {
        'unigram': TOP_CUT_UNI,
        'bigram': TOP_CUT_BI,
        'trigram': TOP_CUT_TRI
    })

total_bigram_dictionary = bigramToDictionary(
    total_selected_gram_table['bigram'])
total_trigram_dictionary = trigramToDictionary(
    total_selected_gram_table['trigram'])

gram_data_content = {
    'subject': collection_name,
    'unigram_freq': total_selected_gram_table['unigram'],
    'bigram_freq': total_selected_gram_table['bigram'],
    'trigram_freq':  total_selected_gram_table['trigram'],
    'bigram_dict': total_bigram_dictionary,
    'trigram_dict': total_trigram_dictionary,
    'interpolation_model': interpolation_model
}

end = time.time()
print("Processing took:", end - start, "seconds")

saveCollectionAsJson(collection_name, gram_data_content)
