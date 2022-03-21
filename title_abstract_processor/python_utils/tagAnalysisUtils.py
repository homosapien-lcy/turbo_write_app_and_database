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
NP = '<DT>?<PRP\$>?<CD>?<RB>*<JJ>*<NN.*>+'
# with modifying verb
NP_with_V = '<DT>?<PRP\$>?<CD>?<VBN>*<VBG>*' + NP[5:]
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
VP = '<MD>*<RB.*>*<VB.*>+'

# defined the regex of an NP pattern
# <NN.*> is any tag in NN category (NNS, NN), etc.
NP_pattern = 'NP: {' + NP_conj_with_prep + '}'
# subject verb object pattern
VP_pattern = 'VP: {' + VP + '}'
SV_pattern = 'SV: {' + NP_conj_with_prep + VP + '}'
# SV_O pattern is an SV pattern with optional O
SV_O_pattern = 'SV_O: {' + NP_conj_with_prep + \
    VP + NP_conj_with_prep_skippable + '}'
# SVO must have O
SVO_pattern = 'SVO: {' + NP_conj_with_prep + VP + NP_conj_with_prep + '}'

NP_regex = nltk.RegexpParser(NP_pattern)
VP_regex = nltk.RegexpParser(VP_pattern)
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


def removeSubject(sentence, keep_placeholder=True):
    tagged_sentence = generateTags(sentence)
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
        # for each word of 'NN*' add it to the noun
        if word[1][:2] in ['NN', 'JJ']:
            noun = word[0] + ' ' + noun
        # else, stop the extraction
        else:
            break

    return noun

# extract nouns from a divided list


def extractNounArr(divided_list):
    return [extractNoun(l) for l in divided_list]


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
