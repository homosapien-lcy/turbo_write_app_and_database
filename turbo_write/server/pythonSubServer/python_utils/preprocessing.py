import string
import re
import math
from collections import Counter

from .percentChar import *
from .IOUtils import *
from .tagAnalysisUtils import *
from .stopWords import *
from .mpUtils import *

from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer

common_chinese_lastnames = set(
    ["wang", "li", "zhang", "liu", "chen", "yang", "huang", "zhao", "wu", "zhou"])

common_figure_id = set(
    [str(i) + j for j in ['a', 'b', 'c', 'd', 'e', 'f'] for i in range(1, 10)])

single_letters = set([str(i) for i in range(97, 123)])

form_of_be = set(["am", "is", "are", "being", "was", "were", "been"])

list_of_pronoun = set(["i", "me", "my", "mine", "myself",
                       "we", "us", "our", "ours", "ourselves",
                       "you", "your", "yours", "yourself", "yourselves",
                       "he", "him", "his", "himself",
                       "she", "her", "hers", "herself",
                       "it", "its", "itself",
                       "they", "them", "their", "theirs", "themselves"
                       ])

et_al_regex = re.compile(r"et al\.")
section_index_regex = re.compile(r"([0-9]\.)+")
reference_regex = re.compile(r"<ref\-list(.*?)>(.*?)<\/ref\-list>")
in_line_reference_tag_regex = re.compile(r"<\/?xref(.*?)>")
html_tag_regex = re.compile(r"<\/?(.*?)>")
html_trans_regex = re.compile(r"&#x(.*?);")
# re.UNICODE for unicode safety
# this contains everything besides alphabets, numbers and _
# this one also keeps greek and other alphabets
# non_alphanumericandconnection_regex = re.compile(r"\W+", re.UNICODE)
# this one is more strict
non_alphanumericandconnectionperiod_regex = re.compile(
    r"[^a-zA-Z0-9_.]+", re.UNICODE)

non_alphaconnection_regex = re.compile(
    r"[^a-zA-Z_]+", re.UNICODE)

# create stemmer for processing
porter_stemmer = PorterStemmer()
snowball_stemmer = SnowballStemmer("english")
snowball_stemmer_ignore_stop = SnowballStemmer(
    "english", ignore_stopwords=True)

# the string.punctuation without '.' and '-' which are still necessary
punct_list_without_junction = '!"#$%&\'()*+,/:;<=>?@[\\]^_`{|}~'
# no _
punct_list_without_connection = '!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~'
# no . - _
punct_list_without_junction_connection = '!"#$%&\'()*+,/:;<=>?@[\\]^`{|}~'
# no .
punct_list_without_period = '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'
# . -
punct_list_junction = '-.'
# equal to string.punctuation
punct_list = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

# cut offs for filtering
digit_percent_cut = 0.1
punct_percent_cut = 0.05
length_cut = 40


def removeChar(s, char):
    return ' '.join(s.split(char))


def removeSpace(s):
    return removeChar(s, ' ')


def removeNull(s):
    return removeChar(s, '\x00')


def removeDigit(s):
    return re.sub(r'[0-9]+', ' ', s)


def removeReferences(s):
    return re.sub(reference_regex, ' ', s)


def removeInLineReferenceTags(s):
    return re.sub(in_line_reference_tag_regex, ' ', s)


def removeHtmltags(s):
    return re.sub(html_tag_regex, ' ', s)


def removeHtmlTrans(s):
    return re.sub(html_trans_regex, ' ', s)


def removeNonAlphaNumericAndConnectionPeriod(s):
    return re.sub(non_alphanumericandconnectionperiod_regex, ' ', s)


def removeNonAlphaAndConnection(s):
    return re.sub(non_alphaconnection_regex, ' ', s)


def removeLineBreaks(s):
    return ' '.join(s.split('\n'))

# leave only 1 space between words


def removeExtraSpace(s):
    return ' '.join(s.split())

# remove extra space for arr


def removeExtraSpaceArr(s_arr):
    return [removeExtraSpace(s) for s in s_arr]

# filter all empty string


def filterEmpty(s_arr):
    return filter(lambda x: len(x.strip()) > 0, s_arr)

# make all '.' to '. '


def fixPeriod(s):
    return removeExtraSpace('. '.join(filterEmpty(s.split('.'))))

# decode & < >


def decodeUrlInfo(s):
    return s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

# find the word with highest frequency in a sentence


def findMostFrequentWord(s):
    return Counter(s.split()).most_common(n=1)[0]


def checkAndJoin(s):
    if not isinstance(s, str):
        return ' '.join(s)
    else:
        return s

# substitute punctuation with space


def subPunct(s, punct_for_removal):
    regex = re.compile('[%s]' % re.escape(punct_for_removal))
    return regex.sub(' ', s)


def subPunctArr(arr, punct_for_removal):
    return [subPunct(x, punct_for_removal) for x in arr]


def subDash(s):
    return s.replace('&#x02013;', '-')

# substitute et als


def subEtAl(text):
    return et_al_regex.sub('et_al', text).strip()

# substitute section indexs


def subSectionIndex(text):
    return section_index_regex.sub('section_index', text).strip()

# element n group
# for example, n = 2: [a1, a2, a3] => [[a1, a2], [a2, a3]]


def elementNGroup(elements, n):
    return zip(*[elements[i:] for i in range(n)])

# preprocessing for making grams


def preprocessForGrams(text):
    # remove digits using regex
    digitless_text = removeDigit(text)
    # remove punctuations
    punctless_text = subPunct(digitless_text)
    # set all to lower case
    return punctless_text.lower()

# convert sentence into BOW


def textToBOW(text):
    preprocess_text = preprocessForGrams(text)
    return preprocess_text.split()

# methods for sentence filtering


def countMaxNNJJs(BOW):
    tags = generateTags(BOW)
    tags = [x[1] for x in tags]
    counts = Counter(tags)
    return max(counts['NN'], counts['JJ'])


# filter sentence with too many NN and JJ
# which drastically slows down the nltk regex searching


def filterTooManyNNJJs(BOWs, cut_off):
    def too_many_lambda(x): return countMaxNNJJs(x) < cut_off
    return list(filter(too_many_lambda, BOWs))


# methods for word filtering


def filterWordsInList(BOW, word_list):
    return [x for x in BOW
            if (x.lower() not in word_list)]


def filterWordsInListArr(BOWs, word_list):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        filterWordsInList_arr = pool.map(
            partial(filterWordsInList, word_list=word_list), BOWs, 1000)
        pool.close()
        pool.join()

    return filterWordsInList_arr


def filterStringsTooShort(string_arr, cut_off):
    return [x for x in string_arr if (len(x) > cut_off)]


def filterStringsTooShortArr(string_arr_arr, cut_off):
    return [filterStringsTooShort(string_arr, cut_off) for string_arr in string_arr_arr]

# remove if length is 1 and is not data and is not a


def filterSingleChar(BOW):
    return list(filter(lambda w: len(w) > 1 or isData(w) or w == 'a', BOW))

# methods for word stemming


def stemWords(BOW, stemmer=snowball_stemmer):
    return [stemmer.stem(x) for x in BOW]


def stemWordsArr(BOWs, stemmer=snowball_stemmer):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        stem_arr = pool.map(partial(stemWords, stemmer=stemmer), BOWs, 1000)
        pool.close()
        pool.join()

    return stem_arr


def allDigits(s):
    return math.floor(percentDigits(s)) == 1


def removeNumericalArr(BOWs):
    return [[x for x in BOW if (not isData(x))] for BOW in BOWs]


def replaceNumerical(s, mark):
    if isData(s):
        return mark
    else:
        return s


def replaceFigure(s, mark):
    s_lower = s.lower().split('.')
    if s_lower[0] == 'figure' or s_lower[0] == 'fig':
        return mark
    else:
        return s


def replaceBe(s, mark):
    s_lower = s.lower()
    if s_lower in form_of_be:
        return mark
    else:
        return s


def replacePronoun(s, mark):
    s_lower = s.lower()
    if s_lower in list_of_pronoun:
        return mark
    else:
        return s


def replaceNumericalArrHelper(BOW, mark="D_A_T_A"):
    return [replaceNumerical(x, mark) for x in BOW]


def replaceNumericalArr(BOWs, mark):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        replaceNumerical_arr = pool.map(
            partial(replaceNumericalArrHelper, mark=mark), BOWs, 1000)
        pool.close()
        pool.join()

    return replaceNumerical_arr


def replaceFigureArrHelper(BOW, mark="F_I_G_U_R_E"):
    return [replaceFigure(x, mark) for x in BOW]


def replaceFigureArr(BOWs, mark):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        replaceFigure_arr = pool.map(
            partial(replaceFigureArrHelper, mark=mark), BOWs, 1000)
        pool.close()
        pool.join()

    return replaceFigure_arr


def replaceBeArrHelper(BOW, mark):
    return [replaceBe(x, mark) for x in BOW]


def replaceBeArr(BOWs, mark):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        replaceBe_arr = pool.map(
            partial(replaceBeArrHelper, mark=mark), BOWs, 1000)
        pool.close()
        pool.join()

    return replaceBe_arr


def replacePronounArrHelper(BOW, mark):
    return [replacePronoun(x, mark) for x in BOW]


def replacePronounArr(BOWs, mark):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_8) as pool:
        replacePronoun_arr = pool.map(
            partial(replacePronounArrHelper, mark=mark), BOWs, 1000)
        pool.close()
        pool.join()

    return replacePronoun_arr


def BOWToDoc(BOW):
    return ' '.join(BOW)


def BOWToDocArr(BOWs):
    return [BOWToDoc(BOW) for BOW in BOWs]

# convert doc to sentences


def docToSentences(fn):
    text = readTxt(fn)

    text = bytes(text, 'utf-8').decode('utf-8',
                                       'ignore').encode('ascii', errors='ignore').decode()

    # remove null bytes
    text = removeNull(text)
    # remove et al
    text = subEtAl(text)

    return text.split('.')

# convert array of doc to sentences


def docArrToSentences(list_of_doc):
    sentences = []
    for fn in list_of_doc:
        sentences.extend(docToSentences(fn))

    return sentences

# convert doc to sentences


def nxmlToSentences(fn):
    # read
    nxml_content = readNxml(fn)
    # process
    nxml_content = removeLineBreaks(nxml_content)
    nxml_content = removeReferences(nxml_content)
    nxml_content = removeHtmltags(nxml_content)
    nxml_content = decodeUrlInfo(nxml_content)
    nxml_content = subDash(nxml_content)
    nxml_content = removeHtmlTrans(nxml_content)
    nxml_content = removeNonAlphaNumericAndConnectionPeriod(nxml_content)
    nxml_content = subEtAl(nxml_content)
    nxml_content = subPunct(
        nxml_content, punct_list_without_junction_connection)
    # change all '.' to '. '
    '''
    fix period already contain remove extra space
    do this before wordwise processing because: if a period is not fix
    there can be situations like: ... some extra space.3 boxes... where
    3 is not replace but it should be
    '''
    nxml_content = fixPeriod(nxml_content)

    return nxml_content.split('. ')

# convert array of doc to sentences


def nxmlArrToSentences(list_of_nxml):
    sentences = []
    for fn in list_of_nxml:
        sentences.extend(nxmlToSentences(fn))

    return sentences

# method that joins all preprocessings
# from txt files to processed docs


def processDocs(list_of_files, use_stemmer, file_reading_fun=docArrToSentences,
                stop_words_option="whole", return_BOWs=False):
    sentences = file_reading_fun(list_of_files)

    # remove empty spaces on two sides
    sentences = [s.strip() for s in sentences]
    # everything lower case
    sentences = [s.lower() for s in sentences]
    # remove all punctuations
    sentences = subPunctArr(sentences, punct_list)
    # fix the line separated words
    sentences = [''.join(s.split('- ')) for s in sentences]
    sentences = [''.join(s.split(' -')) for s in sentences]

    '''
    filter sentences
    '''
    # remove the sentences that have too much digit or punctuation
    # component: a sign for formula or not actual sentence
    sentences = list(filter(lambda s: percentDigits(s)
                            < digit_percent_cut, sentences))
    sentences = list(filter(lambda s: percentPunct(s)
                            < punct_percent_cut, sentences))
    # filter by length
    sentences = list(filter(lambda s: len(s) > length_cut, sentences))
    # filter out citations (et al)
    sentences = list(filter(lambda s: s[-5:] != "et al", sentences))
    # filter out sentences that has same word appear more than 3 times
    '''
    put filter here instead of the BOW section because:
    after substitution (such as P_R_O_N_O_U_N or D_A_T_A), some
    stuffs may be filtered unwantedly
    '''
    sentences = list(
        filter(lambda s: findMostFrequentWord(s)[1] <= 3, sentences))

    # save the sentences that pass the above filters
    writeFile(sentences, "database.txt")

    # tokenize the sentences
    BOWs = tokenizeArr(sentences)

    # filter out sentences with too many NN and JJ present
    BOWs = filterTooManyNNJJs(BOWs, 15)

    '''
    replace data and figures
    '''
    # replace all the numerical data
    BOWs = replaceNumericalArr(BOWs, "D_A_T_A")
    # replace all figures
    BOWs = replaceFigureArr(BOWs, "F_I_G_U_R_E")
    # replace all bes
    BOWs = replaceBeArr(BOWs, "be")
    # replace all pronouns
    BOWs = replacePronounArr(BOWs, "P_R_O_N_O_U_N")

    # remove all stop words according to command
    if stop_words_option.lower() == "whole":
        print("use the whole stopwords list")
        BOWs = filterWordsInListArr(BOWs, stop_words_whole)
    elif stop_words_option.lower() == "small":
        print("use the small stopwords list")
        BOWs = filterWordsInListArr(BOWs, determiners)
    else:
        print("use no stopwords list")

    # filter common Chinese lastnames
    BOWs = filterWordsInListArr(BOWs, common_chinese_lastnames)
    # filter common figure ids
    BOWs = filterWordsInListArr(BOWs, common_figure_id)
    # filter single letters
    BOWs = filterWordsInListArr(BOWs, single_letters)

    # stem words
    if use_stemmer.lower() == "porter":
        print("use porter stemmer")
        BOWs = stemWordsArr(BOWs, porter_stemmer)
    elif use_stemmer.lower() == "snowball":
        print("use snowball stemmer")
        BOWs = stemWordsArr(BOWs, snowball_stemmer)
    elif use_stemmer.lower() == "snowball_ignore_stop":
        print("use snowball stemmer that ignores stop word")
        BOWs = stemWordsArr(BOWs, snowball_stemmer_ignore_stop)
    elif use_stemmer.lower() == "none":
        print("use no stemmer")
    else:
        print("cannot recognize your option, use default (use no stemmer)")

    # if return BOW form
    if return_BOWs:
        return BOWs

    # else, convert to docs
    processed_docs = BOWToDocArr(BOWs)

    return processed_docs

# apply a list of processors to sentence


def wordWiseProcessing(text, list_of_processors):
    BOW = text.split()
    for p in list_of_processors:
        BOW = p(BOW)

    processed_text = ' '.join(BOW)
    processed_text = processed_text.strip()

    return processed_text

# lightly process content, for POS tagging and SVO


def lightlyProcessContent(nxml_input):
    # process
    nxml_content = removeLineBreaks(nxml_input)
    nxml_content = removeReferences(nxml_content)
    nxml_content = removeHtmltags(nxml_content)
    nxml_content = decodeUrlInfo(nxml_content)
    nxml_content = subDash(nxml_content)
    nxml_content = removeHtmlTrans(nxml_content)
    # change all '.' to '. '
    '''
    fix period already contain remove extra space
    do this before wordwise processing because: if a period is not fix
    there can be situations like: ... some extra space.3 boxes... where
    3 is not replace but it should be
    '''
    nxml_content = fixPeriod(nxml_content)
    nxml_content += '.'

    return nxml_content

# process nxml content for fasttext or tfidf training


def processNxmlContent(nxml_input):
    # process
    nxml_content = removeLineBreaks(nxml_input)
    nxml_content = removeReferences(nxml_content)
    nxml_content = removeHtmltags(nxml_content)
    nxml_content = decodeUrlInfo(nxml_content)
    nxml_content = subDash(nxml_content)
    nxml_content = removeHtmlTrans(nxml_content)
    nxml_content = removeNonAlphaNumericAndConnectionPeriod(nxml_content)
    nxml_content = subEtAl(nxml_content)
    nxml_content = subPunct(nxml_content, punct_list_without_period)
    # change all '.' to '. '
    '''
    fix period already contain remove extra space
    do this before wordwise processing because: if a period is not fix
    there can be situations like: ... some extra space.3 boxes... where
    3 is not replace but it should be
    '''
    nxml_content = fixPeriod(nxml_content)
    nxml_content = nxml_content.lower()
    nxml_content = wordWiseProcessing(
        nxml_content, [filterSingleChar, replaceFigureArrHelper, replaceNumericalArrHelper])
    # since D_A_T_A and F_I_G_U_R_E are caps, need to convert to lower again
    nxml_content = nxml_content.lower()
    nxml_content += '.'

    return nxml_content

# process nxml content arr


def processNxmlContentArrSP(nxml_input_arr):
    nxml_content_arr = map(processNxmlContent, nxml_input_arr)
    return list(nxml_content_arr)


def processNxmlContentArrMP(nxml_input_arr):
    # use parallelism to speed up
    # 4 processors are almost as fast as 8
    with eval(core_pool_4) as pool:
        nxml_content_arr = pool.map(processNxmlContent, nxml_input_arr, 1000)
        pool.close()
        pool.join()

    return nxml_content_arr

# process query for embedding


def processSimilaritySearchQuery(query):
    # remove all puncts
    processed_query = removeNonAlphaNumericAndConnectionPeriod(query)
    processed_query = subPunct(query, punct_list_without_connection)
    processed_query = processed_query.lower()
    processed_query = wordWiseProcessing(
        processed_query, [filterSingleChar, replaceFigureArrHelper, replaceNumericalArrHelper])
    # since D_A_T_A and F_I_G_U_R_E are caps, need to convert to lower again
    processed_query = processed_query.lower()
    return processed_query


def readAndProcessNxmlFileHelper(nxml_fn):
    # read
    nxml_content = readNxml(nxml_fn)
    # process
    nxml_content = processNxmlContent(nxml_content)

    return nxml_content

# process nxml files with multicore


def readAndProcessNxmlFilesMP(nxml_fn_list):
    # use parallelism to speed up, use 1000 as chunk size
    with eval(core_pool_4) as pool:
        nxml_content_arr = pool.map(
            readAndProcessNxmlFileHelper, nxml_fn_list, 1000)
        pool.close()
        pool.join()

    return nxml_content_arr


def elementNGroup(elements, n):
    return zip(*[elements[i:] for i in range(n)])

# clean up segment


def cleanUpSegment(segment):
    # the segment may has line break and space on two ends, thus strip
    s = segment.strip()
    s = subPunct(s, punct_list_without_connection)
    # remove non alphanumerics
    s = removeNonAlphaNumericAndConnectionPeriod(s)
    # remove extra space left by subpunct
    s = removeExtraSpace(s)
    return s

# load sentence database from file


def loadSentenceDB(filename, segment_deliminator='pe'):
    if segment_deliminator == 'pe':
        # if deliminate by period, read everything and remove periods
        sentence_DB = readWholeFile(filename)
        sentence_DB = sentence_DB.split('. ')
    else:
        # if deliminate by line break, read line by line to prevent memory error
        DB_file = open(filename, 'r')
        sentence_DB = []
        for segment in DB_file:
            sentence_DB.append(cleanUpSegment(segment))

        DB_file.close()

    return sentence_DB

# convert extracted pattern into phrase


def extractedPatternToPhrase(extracted):
    # join into phrase
    words = [x[0] for x in extracted]
    phrase = ' '.join(words)

    # clean up
    # remove non alpha numerics and punct
    phrase = removeNonAlphaNumericAndConnectionPeriod(phrase)
    phrase = subPunct(phrase, punct_list_without_connection)
    # lower case
    phrase = phrase.lower()
    # remove extra space left by subpunct
    phrase = removeExtraSpace(phrase)

    return phrase
