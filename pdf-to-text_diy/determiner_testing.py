import sys
from python_utils.IOUtils import *
from python_utils.determinerSuggestion import *
from python_utils.preprocessing import *

text_fn = sys.argv[1]

# read in file
sentences = docToSentences(text_fn)

# convert to sentence tags
tagged_sentences = generateTagsArr(sentences)

# find all NPs in those sentences
NP_parsed_sentences = parseSentences(tagged_sentences, findNP)

# generate suggestions
suggestions = suggestDTArr(NP_parsed_sentences)

for ps, seg, DT_suggestion in suggestions:
    print("for sentence: ", ps)
    print("in segment: ", seg)
    print("suggest: ", DT_suggestion)
