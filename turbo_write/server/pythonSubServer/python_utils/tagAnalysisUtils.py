from more_itertools import chunked, flatten
import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import cmudict
# load cmu pronunciation dictionary for sound look up
pronunciation_dict = cmudict.dict()
vowels = "AEIOUaeiou"

import inflect
inflect = inflect.engine()

from .mpUtils import *

# pattern definition
# a pattern that is too complicated is not good,
# since the matching may not be nice
# it must contain at least 1 NN
NP = '<PDT>?<DT>?<PRP\$>?<CD>?<RB>*<JJ.*>*<NN.*>+'
# with modifying verb
NP_with_V = '<PDT>?<DT>?<PRP\$>?<CD>?<VB.*>*' + NP[5:]
NP_with_V_skippable = NP_with_V[:-1] + '*'
# use star for the last NN, since NN after CC is optional
NP_conj = NP_with_V + '<CC>?' + NP_with_V_skippable
NP_conj_skippable = NP_with_V_skippable + '<CC>?' + NP_with_V_skippable
# with preposition, allow 4 segments in total
# more than 4 are considerred bad sentences
NP_conj_with_prep = NP_conj + '<IN>?' + NP_conj_skippable + '<IN>?' + \
    NP_conj_skippable + '<IN>?' + NP_conj_skippable
# skippable use * and ? for all tags, and thus may or may not appear
NP_conj_with_prep_skippable = NP_conj_skippable + '<IN>?' + NP_conj_skippable + \
    '<IN>?' + NP_conj_skippable + '<IN>?' + NP_conj_skippable

# MD: could, will
# <VB.*>+<JJ.*>*<IN>? covers "is(VBZ) better(JJR) than(IN)" case
# leaving out DT to prevent "is(VBZ) better(JJR) than(IN) the(DT) fresh(JJ) XX(NN)" in which JJ belongs to the next NN
# <NN*>* is important for cases like "have(VB.*) great(JJ.*) influence(NN.*) on(IN)"
# could(MD) be(VB.*) beneficial(JJ.*) compared(VB.*) with(IN)
# along(IN) with(IN)
VP = '<MD>*<RB.*>*<VB.*>+<JJ.*>*<VB.*>*<NN.*>*<IN>*<TO>?'
relation_VP = '<MD>*<RB.*>*<VB.*>+<JJ.*>*<VB.*>*<NN.*>*<IN>*<TO>?<RB.*>*<JJ.*>*'

# defined the regex of an NP pattern
# <NN.*> is any tag in NN category (NNS, NN), etc.
NP_pattern = 'NP: {' + NP_conj_with_prep + '}'
# subject verb object pattern
VP_pattern = 'VP: {' + VP + '}'
relation_VP_pattern = 'relation_VP: {' + relation_VP + '}'
SV_pattern = 'SV: {' + NP_conj_with_prep + VP + '}'
# SV_O pattern is an SV pattern with optional O
SV_O_pattern = 'SV_O: {' + NP_conj_with_prep + \
    VP + NP_conj_with_prep_skippable + '}'
# SVO must have O
SVO_pattern = 'SVO: {' + NP_conj_with_prep + VP + NP_conj_with_prep + '}'

NP_regex = nltk.RegexpParser(NP_pattern)
VP_regex = nltk.RegexpParser(VP_pattern)
relation_VP_regex = nltk.RegexpParser(relation_VP_pattern)
SV_regex = nltk.RegexpParser(SV_pattern)
SV_O_regex = nltk.RegexpParser(SV_O_pattern)
SVO_regex = nltk.RegexpParser(SVO_pattern)

# check whether a noun is singular
# inflect.singular_noun can handle compound
# nouns such as "our chromosomes"


def isSingular(word):
    # if the word is plural, it will
    # return a singular form
    if inflect.singular_noun(word):
        return False
    # if the word is already singular, it
    # will return False, and thus should return
    # True
    else:
        return True


# check whether a word starts with vowel sound


def startsWithVowel(word, heuristic=False):
    # if heuristic, only check whether word starts with
    # vowel characters
    if heuristic:
        return (word[0] in vowels)
    else:
        # only take the first part of compound word
        # to increase success matching
        word = word.split('-')[0]

        # isupper return true only when all letters
        # are upper
        if word.isupper():
            # for all cap words, the pronunciation is
            # the reading of each letter, thus should
            # look up only the first letter
            word = word[0]

        # pronunciation_dict has keys in lower case
        word = word.lower()

        # if not in the pronunciation_dict, only check
        # whether word starts with
        # vowel characters
        if word not in pronunciation_dict:
            return (word[0] in vowels)
        # else, check the pronunciation
        else:
            pronunciation = pronunciation_dict[word]
            return (pronunciation[0][0][0] in vowels)

# check wether the token is string before tokenize


def checkAndTokenize(input):
    # if string, tokenize
    if isinstance(input, str):
        return word_tokenize(input)

    # else, return as it is
    return input


def tokenizeArr(sentences):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        token_arr = pool.map(word_tokenize, sentences, 1000)
        pool.close()
        pool.join()

    return token_arr


def generateTags(sentence):
    return pos_tag(checkAndTokenize(sentence))


def generateTagsArr(sentences):
    return [generateTags(sentence) for sentence in sentences]

# find all nouns and verbs in a sentence


def findNounsAndVerbs(tag_arr):
    arr = []

    current_noun = ""
    noun_mode = False

    current_verb = ""
    verb_mode = False

    for i in range(0, len(tag_arr)):
        current_tag = tag_arr[i]
        # if noun category
        if current_tag[1][0:2] == "NN":
            current_noun += current_tag[0] + " "
            noun_mode = True
        else:
            if noun_mode:
                # add word except the last space
                arr.append((current_noun[:-1], "NN"))
                current_noun = ""

            noun_mode = False

        # if verb cateory
        if current_tag[1][0:2] == "VB":
            current_verb += current_tag[0] + " "
            verb_mode = True
        else:
            if verb_mode:
                # add the by, after, before, for, to, in, etc. into the verb
                # TO: to
                # IN: after, before, by, for, in
                if current_tag[1] == "IN" or current_tag[1] == "TO":
                    current_verb += current_tag[0] + " "

                # add word except the last space
                arr.append((current_verb[:-1], "VB"))
                current_verb = ""

            verb_mode = False

    return arr

# find a chosen pattern


def findPattern(sentence, pattern_regex):
    return pattern_regex.parse(sentence)

# find a NP pattern


def findNP(sentence):
    return findPattern(sentence, NP_regex)

# find a VP pattern


def findVP(sentence):
    return findPattern(sentence, VP_regex)

# find a relation VP pattern


def findRelationVP(sentence):
    return findPattern(sentence, relation_VP_regex)

# find a SV pattern


def findSV(sentence):
    return findPattern(sentence, SV_regex)

# find a SVO pattern


def findSV_O(sentence):
    return findPattern(sentence, SV_O_regex)

# find a SVO pattern


def findSVO(sentence):
    return findPattern(sentence, SVO_regex)

# apply a pattern finding operator


def parseSentences(sentences, operator):
    return [operator(sentence) for sentence in sentences]

# find the part of tree


def findSentencePart(parsed_sentence, part):
    return list(parsed_sentence.subtrees(lambda t: t.label() == part))

# find parts of all sentences


def findSentencePartArr(parsed_sentence_arr, part):
    temp = [findSentencePart(ps, part) for ps in parsed_sentence_arr]
    temp = list(filter(lambda x: len(x) > 0, temp))
    return temp

# remove the subjects from a sentence


def removeSubject(sentence, tag_operator=generateTags, keep_placeholder=True):
    tagged_sentence = tag_operator(sentence)
    SV_marked_sentence = findSV(tagged_sentence)
    # loop through the sub trees
    for tree in SV_marked_sentence.subtrees():
        # find a SV pattern
        if tree.label() == "SV":
            '''
            the code below can't do the trick, has to
            modify leaf by accessing tree[tree.leaf_treeposition(i)]
            '''
            '''
            for leaf in tree.leaves():
                leaf = ("", leaf[1])
            '''
            num_SV_leaves = len(tree.leaves())
            # in each SV, only replace the first word to
            # "S_U_B_J_E_C_T", others to "" (empty)
            # set initial already_replaced to not keep_placeholder:
            # if false, already_replaced start as true and thus not
            # keeping any place holder
            already_replaced = not keep_placeholder
            for i in range(0, num_SV_leaves):
                # keep if the leaf is a verb
                if tree[tree.leaf_treeposition(i)][1][:2] not in ["VB", "MD"]:
                    # else, set the node value to empty
                    if not already_replaced:
                        tree[tree.leaf_treeposition(i)] = (
                            "S_U_B_J_E_C_T", tree[tree.leaf_treeposition(i)][1])
                        already_replaced = True
                    else:
                        tree[tree.leaf_treeposition(i)] = (
                            "", tree[tree.leaf_treeposition(i)][1])

    # collect the words and remove empty
    subject_removed_sentence = [
        l[0] for l in SV_marked_sentence.leaves() if (len(l[0]) != 0)]

    # joins the leaf words and return
    return subject_removed_sentence


def removeSubjectArr(sentences, keep_placeholder=True):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        remove_subject_arr = pool.map(
            partial(removeSubject, keep_placeholder=keep_placeholder), sentences, 1000)

    return remove_subject_arr

# divide the list of NP leaves by segmenting
# 'CC' and 'IN'


def divideNPLeaves(NP_leaves):
    divided_lists = []
    each_list = []
    for i in range(0, len(NP_leaves)):
        leaf = NP_leaves[i]
        # if 'CC' or 'IN', divide list
        if leaf[1] == 'CC' or leaf[1] == 'IN':
            # if not empty, add to list
            if len(each_list) > 0:
                divided_lists.append(each_list)

            # clear the list
            each_list = []
        # for other words, add to output
        else:
            each_list.append(leaf)

    # append the last element
    if len(each_list) > 0:
        divided_lists.append(each_list)

    return divided_lists


# extract noun from a NP


def extractNoun(each_list):
    rl = list(reversed(each_list))
    # no matter the property of the last word
    # add it to the noun
    '''
    since all words before 'IN' and 'CC' are
    indeed nouns, their other assignment are
    bug of the tagger
    '''
    noun = rl[0][0]
    for word in rl[1:]:
        # for each word of 'NN.*' add it to the noun
        if word[1][:2] in ['NN', 'JJ']:
            noun = word[0] + ' ' + noun
        # else, stop the extraction
        else:
            break

    return noun

# extract nouns from a divided list


def extractNounArr(divided_list):
    return [extractNoun(l) for l in divided_list]

# convert subtree to annotated segment


def subtreeToSegment(tree):
    target_segment = []
    num_leaves = len(tree.leaves())
    for i in range(0, num_leaves):
        # keep if the leaf is a verb
        target_segment.append(tree[tree.leaf_treeposition(i)])

    return target_segment

# check for JJ.* followed by NN.* condition
# remove JJ.* if followed by NN.*


def removeJJIfFollowByNN(target_segment, next_segment):
    # check and convert tree if needed
    if type(next_segment) is nltk.tree.Tree:
        next_token = subtreeToSegment(next_segment)[0]
    else:
        next_token = next_segment

    # if JJ.* followed by NN.*, remove last
    if next_token[1][:2] == "NN" and target_segment[-1][1][:2] == "JJ":
        return target_segment[:-1]

    # else, return original
    return target_segment

# extract segment from a sentence


def extractPattern(sentence, target_pattern, tag_operator):
    tagged_sentence = tag_operator(sentence.strip())
    marked_sentence = findPattern(
        tagged_sentence, nltk.RegexpParser(target_pattern))
    pattern_name = target_pattern.split(':')[0]
    # loop through the sub trees and collect
    target_segment_arr = []
    for (i, part) in enumerate(marked_sentence):
        # only process trees
        if type(part) is nltk.tree.Tree:
            # check that the pattern match
            if part.label() == pattern_name:
                # convert to segments
                target_segment = subtreeToSegment(part)

                # for patterns end with VP
                if pattern_name == "VP" or pattern_name == "SV" or pattern_name == "relation_VP":
                    # if not the last part, need to check for
                    # JJ.* followed by NN.* condition
                    if i < len(marked_sentence) - 1:
                        next_segment = marked_sentence[i+1]
                        target_segment = removeJJIfFollowByNN(
                            target_segment, next_segment)

                target_segment_arr.append(target_segment)

    return target_segment_arr

# extract segment from a sentence,
# if two patterns are right next to each other, join them


def extractPatternAndJoinNeighbor(sentence, target_pattern, tag_operator):
    tagged_sentence = tag_operator(sentence.strip())
    marked_sentence = findPattern(
        tagged_sentence, nltk.RegexpParser(target_pattern))
    pattern_name = target_pattern.split(':')[0]
    # loop through the sub trees and collect
    target_segment_arr = []
    # record previous pattern index for joining neighbors
    previous_pattern_index = -float("inf")
    for (i, part) in enumerate(marked_sentence):
        # only process trees
        if type(part) is nltk.tree.Tree:
            # check that the pattern match
            if part.label() == pattern_name:
                # convert to segments
                target_segment = subtreeToSegment(part)

                # for patterns end with VP
                if pattern_name == "VP" or pattern_name == "SV" or pattern_name == "relation_VP":
                    # if not the last part, need to check for
                    # JJ.* followed by NN.* condition
                    if i < len(marked_sentence) - 1:
                        next_segment = marked_sentence[i+1]
                        target_segment = removeJJIfFollowByNN(
                            target_segment, next_segment)

                # if it's the previous segment
                if previous_pattern_index + 1 == i:
                    last_segment = target_segment_arr.pop()
                    # last_segment + target_segment basically
                    # extend the last_segment from the front of target_segment
                    target_segment = last_segment + target_segment

                target_segment_arr.append(target_segment)
                previous_pattern_index = i

    return target_segment_arr

# retrieve pos tages from spacy


def runSpacyTagger(spacy_model, sentence):
    results = spacy_model(sentence)
    pos_tags = [(word.text, word.tag_) for word in results]
    return pos_tags

# retrieve pos tages from stanfordnlp


def runStanfordNLPTagger(stanford_pipeline, sentence):
    results = stanford_pipeline(sentence).sentences[0].words
    pos_tags = [(word.text, word.xpos) for word in results]
    return pos_tags


# format RDR tag to tag array format


def RDRTagsFormatter(RDR_tag_sentence):
    RDR_tag_arr = []
    RDR_tags = RDR_tag_sentence.split()
    for tag in RDR_tags:
        tag_segs = tag.split('/')
        RDR_tag_arr.append(('/'.join(tag_segs[:-1]), tag_segs[-1]))

    return RDR_tag_arr

# generate RDR tags


def generateRDRTags(RDRPOSTagger, sentence):
    RDR_pos_tags = RDRPOSTagger.tagRawSentence('self', sentence)
    return RDRTagsFormatter(RDR_pos_tags)

# run on the sentence with all taggers


def runAllTaggers(sentence, taggers_dictionary):
    result_dictionary = {}
    for key in taggers_dictionary.keys():
        tagger = taggers_dictionary[key]
        result_dictionary[key] = tagger(sentence)

    return result_dictionary

# run parsing with all taggers


def parseWithAllTaggers(sentence, taggers_dictionary):
    result_dictionary = {}
    for key in taggers_dictionary.keys():
        tagger = taggers_dictionary[key]
        result_dictionary[key] = findRelationVP(tagger(sentence))

    return result_dictionary


def printDictionary(dict):
    for key in dict.keys():
        print(key)
        print(dict[key])

# extract pattern for single processor


def extractPatternArrSP(sentence_arr, target_pattern,
                        tag_operator, extractPatternOperator=extractPatternAndJoinNeighbor):
    extracted = map(lambda s: extractPatternOperator(
        s, target_pattern, tag_operator), sentence_arr)
    return list(flatten(extracted))

# extract pattern for multi processor


def extractPatternArrMP(sentence_arr, target_pattern,
                        tag_operator, extractPatternOperator=extractPatternAndJoinNeighbor):
    with eval(core_pool_4) as pool:
        extracted = pool.map(partial(extractPatternOperator,
                                     target_pattern=target_pattern,
                                     tag_operator=tag_operator),
                             sentence_arr, 1000)
        pool.close()
        pool.join()

        return list(flatten(extracted))


'''
def test_removeSubject():
    sentence_1 = "biology watches a movie and sleep"
    sentence_2 = "chromosome is a very important thing"
    sentence_3 = "chromosome is a very important thing that watches movie"
    sentence_4 = "chromosome is a very important thing which, as a friend, the friendly chromosomes recommend to me"

    print("with placeholder: ")
    print(removeSubject(sentence_1))
    print(removeSubject(sentence_2))
    print(removeSubject(sentence_3))
    print(removeSubject(sentence_4))
    print(removeSubjectArr([sentence_1, sentence_2]))

    print("without placeholder: ")
    print(removeSubject(sentence_1, keep_placeholder=False))
    print(removeSubject(sentence_2, keep_placeholder=False))
    print(removeSubject(sentence_3, keep_placeholder=False))
    print(removeSubject(sentence_4, keep_placeholder=False))
    print(removeSubjectArr([sentence_1, sentence_2], keep_placeholder=False))


test_removeSubject()
'''

'''
def test_startsWithVowel():
    words = [
        "hour", 
        "hours", 
        "great", 
        "alpha", 
        "europe",
        "yolk",
        "our"
    ]

    for w in words:
        print("word: ", w)
        print(startsWithVowel(w))
        print(startsWithVowel(w, heuristic=False))
        print(startsWithVowel(w, heuristic=True))

test_startsWithVowel()
'''

'''
from RDRPOSTagger import *
RDRPOSTagger = RDRPOSTagger()
RDRPOSTagger.englishSetup()


def runGenerateRDRTag(sentence):
    return generateRDRTags(RDRPOSTagger, sentence)


def test_extractPatternAndJoinNeighbor():
    a = " CREB-regulated gene expression has been shown to be downregulated in AD brain."
    print(extractPattern(
        a, relation_VP_pattern, runGenerateRDRTag))
    print(extractPatternAndJoinNeighbor(
        a, relation_VP_pattern, runGenerateRDRTag))

    b = " CREB-regulated gene expression has been shown to ffffff be downregulated in AD brain."
    print(extractPattern(
        b, relation_VP_pattern, runGenerateRDRTag))
    print(extractPatternAndJoinNeighbor(
        b, relation_VP_pattern, runGenerateRDRTag))

    c = " CREB-regulated gene expression has been shown to be downregulated in AD brain CREB-regulated gene expression has been shown to be downregulated in AD brain."
    print(extractPattern(
        c, relation_VP_pattern, runGenerateRDRTag))
    print(extractPatternAndJoinNeighbor(
        c, relation_VP_pattern, runGenerateRDRTag))


test_extractPatternAndJoinNeighbor()
'''

'''
from RDRPOSTagger import *
RDRPOSTagger = RDRPOSTagger()
RDRPOSTagger.englishSetup()


def runGenerateRDRTag(sentence):
    return generateRDRTags(RDRPOSTagger, sentence)


def test_extractPatternArr():
    a = " CREB-regulated gene expression has been shown to be downregulated in AD brain."
    b = " CREB-regulated gene expression has been shown to ffffff be downregulated in AD brain."
    c = " CREB-regulated gene expression has been shown to be downregulated in AD brain CREB-regulated gene expression has been shown to be downregulated in AD brain."

    s_arr = [a, b, c]
    print(list(extractPatternArrSP(s_arr, relation_VP_pattern, runGenerateRDRTag)))
    print(list(extractPatternArrMP(s_arr, relation_VP_pattern, runGenerateRDRTag)))
    print(list(extractPatternArrSP(s_arr, relation_VP_pattern,
                              runGenerateRDRTag, extractPattern)))
    print(list(extractPatternArrMP(s_arr, relation_VP_pattern,
                              runGenerateRDRTag, extractPattern)))


test_extractPatternArr()
'''
