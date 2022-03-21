import sys
from python_utils.IOUtils import *
from python_utils.determinerSuggestion import *
from python_utils.preprocessing import *

text_fn = sys.argv[1]

# read in file
sentences = docToSentences(text_fn)

no_reference = []
for i in range(0, len(sentences)):
    s = sentences[i]
    if s[:10] == "References":
        break

    no_reference.append(s)

sentences = no_reference

# convert to sentence tags
tagged_sentences = generateTagsArr(sentences)

# find all NPs in those sentences
NP_parsed_sentences = parseSentences(tagged_sentences, findNP)

# generate suggestions
suggestions = suggestDTArr(NP_parsed_sentences)

for ps, seg, DT_suggestion in suggestions:
    if DT_suggestion:
        s = ' '.join([l[0] for l in ps.leaves()])
        print("for sentence: ", s)
        print("in segment: ", seg)
        print("suggest: ", DT_suggestion)
