# nltk tagger
from python_utils.tagAnalysisUtils import *

import spacy
# use gpu for the task
# gpu is actually slower (about 3 times) during tagging inference... 
#spacy.prefer_gpu()
spacy_model = spacy.load('en_core_web_sm')

from RDRPOSTagger import *
RDRPOSTagger = RDRPOSTagger()
RDRPOSTagger.englishSetup()

import stanfordnlp
# set tokenize_pretokenized=True for only tokenize by whitespace
stanfordnlp_config = {
    'processors': 'tokenize,pos',
    'tokenize_pretokenized': True
}
# use default language en and process until pos
stanfordnlpTagger = stanfordnlp.Pipeline(**stanfordnlp_config)

sentence_DB_fn = sys.argv[1]

taggers_dictionary = {
    "nltk": generateTags,
    "RDR": lambda s: generateRDRTags(RDRPOSTagger, s),
    "spacy": lambda s: runSpacyTagger(spacy_model, s),
    "stanfordnlp": lambda s: runStanfordNLPTagger(stanfordnlpTagger, s)}

'''
test_sentence_1 = "treatments were dry matter basis d_a_t_a non leymus chinensis hay diet nlc d_a_t_a cs d_a_t_a ah and d_a_t_a added leymus chinensis hay diet alc d_a_t_a cs d_a_t_a ah d_a_t_a leymus chinensis hay d_a_t_a adding leymus chinensis hay increased neutral detergent fiber content and in vitro digestibility of the diet"
test_sentence_2 = "no author has a financial or proprietary interest in any material or method mentioned"
test_sentence_3 = "preoperative visual disability was significantly higher in patients awaiting cataract surgery in both eyes than in those awaiting second eye surgery"
test_sentence_4 = "the surgical outcome measures were logmar visual acuities and the rasch refined vsq"
test_sentence_5 = "hdl was elevated with reconstituted high density lipoprotein rhdl d_a_t_a cardiac repolarization was studied by recording cardiac transmembrane potentials with the patch clamp technique from isolated rabbit cardiomyocytes that were superfused with rhdl"
test_sentence_6 = "a fried egg is placed in the pan for 10 minutes"

test_arr = [test_sentence_1, test_sentence_2,
            test_sentence_3, test_sentence_4,
            test_sentence_5, test_sentence_6]

for s in test_arr:
    print(s)
    result_dict = runAllTaggers(s, taggers_dictionary)
    printDictionary(result_dict)
'''

sentence_DB_file = open(sentence_DB_fn, 'r')
for segment in sentence_DB_file:
    sentences = segment.split('. ')
    for s in sentences:
        print(s)
        printDictionary(parseWithAllTaggers(s, taggers_dictionary))


sentence_DB_file.close()
