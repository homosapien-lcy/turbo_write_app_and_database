import re
import string
import nltk
from .preprocessing import *
from .counterHelper import *
from collections import Counter

# allow words of all size
word_size_cut = 4

# list of words that should not be in the count
#filter_list = ['a', 'the', 'of', 'to', 'is', 'for', 'it', 'and']
filter_list = []

# convert collection into frequency table


def templateToTable(template):
    table = Counter([])
    for i in range(0, len(template)):
        cur = template[i]
        cur_phr = cur['phrase']
        cur_freq = cur['frequency']

        table[cur_phr] = cur_freq

    return table


def collectGramsFromDBResponse(DBResponse):
    temp = {
        'unigram': Counter([]),
        'bigram': Counter([]),
        'trigram': Counter([])
    }

    for dict in DBResponse:
        temp['unigram'] += dict['unigram_freq']
        temp['bigram'] += dict['bigram_freq']
        temp['trigram'] += dict['trigram_freq']

    return temp

# find the lead to the word and the current word


def generateLeadAndCur(phrase, N):
    word_component = phrase.split()
    lead = ''
    for i in range(0, N - 1):
        lead += word_component[i] + ' '

    # remove the last empty space ' '
    return lead[:-1], word_component[-1]

# method to generate dictionary with prev words as keys
# and [phrase, freq] array as items


def gramToDictionary(gram_bag, N):
    gram_dictionary = {}

    for key in gram_bag.keys():
        # lead is the prev words
        lead, cur = generateLeadAndCur(key, N)
        if lead in gram_dictionary:
            # in the order of [phrase, current word, frequency]
            gram_dictionary[lead].append([key, cur, gram_bag[key]])
        else:
            gram_dictionary[lead] = [[key, cur, gram_bag[key]]]

    return gram_dictionary

# generate bigrams from BOW


def BOWToBigram(word_bag):
    bigram_bag = list(nltk.bigrams(word_bag))
    return [' '.join(x) for x in bigram_bag]

# generate trigrams from BOW


def BOWToTrigram(word_bag):
    trigram_bag = list(nltk.trigrams(word_bag))
    return [' '.join(x) for x in trigram_bag]


def bigramToDictionary(bigram_bag):
    return gramToDictionary(bigram_bag, 2)


def trigramToDictionary(trigram_bag):
    return gramToDictionary(trigram_bag, 3)


def generateWordTable(text):
    word_bag = textToBOW(text)

    # generate bi and tri grams
    bigram_bag = BOWToBigram(word_bag)
    trigram_bag = BOWToTrigram(word_bag)

    '''
    only select words not in the filter list
    and size > word_size_cut (remove punctuation and short words)
    for unigram processing, but keep those words in bi and tri, since
    they can be useful as phrases
    '''
    unigram_bag = [x for x in word_bag
                   if (x not in filter_list and len(x) >= word_size_cut)]

    unigram_count = Counter(unigram_bag)
    bigram_count = Counter(bigram_bag)
    trigram_count = Counter(trigram_bag)

    gram_box = {
        'unigram': unigram_count,
        'bigram': bigram_count,
        'trigram': trigram_count
    }

    # print("grams in the uploaded texts")
    # print(gram_box)

    return gram_box
