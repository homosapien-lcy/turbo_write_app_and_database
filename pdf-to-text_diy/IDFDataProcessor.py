'''
this script load the sentence database, generate the idf information and save to file
'''
import time
from python_utils.numericalAnalysisUtils import *
from python_utils.preprocessing import *

sentence_DB_file = sys.argv[1]
min_df = int(sys.argv[2])
subject = sys.argv[3]
segment_deliminator = sys.argv[4]
stop_word_option = sys.argv[5].lower()

# lb = line break, pe = period
if segment_deliminator != 'lb' and segment_deliminator != 'pe':
    print('sentence deliminator not recognized, must be either "lb" or "pe" for line break and period')
    sys.exit(0)

start = time.time()
sentence_DB = loadSentenceDB(sentence_DB_file, segment_deliminator)
print("in total", len(sentence_DB), "segments")
end = time.time()
print("loading takes", end-start, "seconds")

# option for stop words
if stop_word_option == 'determiners':
    stop_word_for_idf = determiners_plus_letters_plus_digits
elif stop_word_option == 'whole':
    stop_word_for_idf = ENGLISH_STOP_WORDS_plus_letters_plus_digits
elif stop_word_option == 'none':
    stop_word_for_idf = letters_plus_digits
else:
    print("stop word option must be 'determiners', 'whole' or 'none'")
    exit(0)

start = time.time()
num_docs,  idf_vocab_dict, idf_stopword_list, idf = calcIDFInfo(
    sentence_DB, min_df, stop_word_for_idf)
end = time.time()
print("processing to IDF takes", end-start, "seconds")

idf_info_dict = {
    'num_docs': num_docs,
    'idf_vocab_dict': idf_vocab_dict,
    'idf_stopword_list': idf_stopword_list,
    'idf': idf
}

savePythonObject(idf_info_dict, subject + '_idf_data_' +
                 stop_word_option + '.pkl')
