import re
from string import punctuation
import wordninja

start_regex = re.compile(r"(<p(.*?)>|<sec(.*?)>|<title(.*?)>|<abstract(.*?)>)")
end_regex = re.compile(r"(<\/p>|<\/sec>|<\/title>|<\/abstract>)")

et_al_regex = re.compile(r"et al\.")
section_index_regex = re.compile(r"([0-9]\.)+")
reference_regex = re.compile(r"<ref\-list(.*?)>(.*?)<\/ref\-list>")
in_line_reference_tag_regex = re.compile(r"<\/?xref(.*?)>")
html_tag_regex = re.compile(r"<\/?(.*?)>")
html_trans_regex = re.compile(r"&#x(.*?);")

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


def removeLineBreaks(s):
    return ' '.join(s.split('\n'))

# leave only 1 space between words


def removeExtraSpace(s):
    return ' '.join(s.split())

# make all '.' to '. '


def fixPeriod(s):
    return removeExtraSpace('. '.join(s.split('.')))

# decode & < >


def decodeUrlInfo(s):
    return s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')


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


def filterWordsTooShort(BOW, cut_off):
    return [x for x in BOW if (len(x) > cut_off)]


def filterWordsTooShortArr(BOWs, cut_off):
    return [filterWordsTooShort(BOW, cut_off) for BOW in BOWs]

# remove if length is 1 and is not data and is not a


def filterSingleChar(BOW):
    return list(filter(lambda w: len(w) > 1 or isData(w) or w == 'a', BOW))

# check whether the current char is in the data category
# this include '-' (-2.8) '.' (0.72) '%' (79%) 'e' (1e-3) and all numbers


def isData(s):
    len_s = len(s)
    for i in range(0, len_s):
        cur_char = s[i]

        if cur_char.isdigit():
            continue

        if cur_char == '-':
            continue

        if cur_char == '%':
            continue

        if cur_char == '.':
            continue

        if cur_char == 'e':
            continue

        return False

    return True


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


def wordWiseProcessing(text, list_of_processors):
    BOW = text.split()
    for p in list_of_processors:
        BOW = p(BOW)

    processed_text = ' '.join(BOW)
    processed_text = processed_text.strip()

    return processed_text


# check whether a word is capitalized


def isCapitalized(s):
    # false for empty
    if len(s) == 0:
        return False

    return s[0].isupper()

# check whether a string start with digit


def startWithDigit(s):
    # false for empty
    if len(s) == 0:
        return False

    return s[0].isdigit()

# check whether a line is section title


def isSectionTitle(this_line, next_line, length_cut=7):
    # false for empty
    if len(this_line) == 0:
        return False

    # check whether this line has the length of a sentence (long)
    # other than length of a title (short)
    longer_than_cut = (len(this_line.split()) > length_cut)
    # whether this line end with period
    end_with_period = (this_line[-1] == ".")
    # whether the next line start with capitalized letter
    next_start_with_capitalized = isCapitalized(next_line)
    # whether the next line start with a digit
    next_start_with_digit = startWithDigit(next_line)

    # if this line not end with period and next line is capitalized or digit
    # very likely to be the title
    if (not end_with_period) and (next_start_with_capitalized or next_start_with_digit):
        # but still have the edge case that the first noun of the
        # next line is a noun that always caps, thus also check for
        # length
        if (not longer_than_cut):
            return True

    return False

# combine all the paragraphs into 1 line


def combineParagraph(text):
    text_lines = text.split('\n')

    combined_text = ""
    # ignore last line, which is definitely not
    # a title
    for i in range(0, len(text_lines)-1):
        this_line = text_lines[i].strip()
        next_line = text_lines[i+1].strip()

        # for title, add an individual line
        if isSectionTitle(this_line, next_line):
            combined_text += '\n' + this_line + '\n'
        else:
            if len(combined_text) > 0:
                # if last line if a word break
                # remove '-'
                if combined_text[-1] == "-":
                    combined_text = combined_text[:-1]

            if len(this_line) > 0:
                combined_text += this_line

    # add the last line
    if len(combined_text) > 0:
        # if last line if a word break
        # remove '-'
        if combined_text[-1] == "-":
            combined_text = combined_text[:-1]

    combined_text += text_lines[-1]

    return combined_text.strip()


# a wrapper method that split word using word ninja


def wordSeparate(chunk):
    # if empty
    if len(chunk) == 0:
        return chunk
    # if all characters
    # add space and return
    elif chunk.isalpha():
        return ' '.join(wordninja.split(chunk))
    # if contain -
    # process each subpart separately and join
    elif '-' in chunk:
        sub_chunks = chunk.split('-')
        sub_chunks = [wordSeparate(sc) for sc in sub_chunks]
        return '-'.join(sub_chunks)
    # else if the only punct is the last character
    # add space to the words and append punct at end
    elif chunk[-1] in punctuation and chunk[:-1].isalpha():
        return ' '.join(wordninja.split(chunk[:-1])) + chunk[-1]
    # else, don't split it and keep the punctuations
    # since wordninja removes puncts
    else:
        return chunk


# add spaces to sentences with words that sticks together
def wordSeparateSentence(sent):
    words = sent.split()
    words = [wordSeparate(w) for w in words]
    return ' '.join(words)

# element n group
# for example, n = 2: [a1, a2, a3] => [[a1, a2], [a2, a3]]


def elementNGroup(elements, n):
    return zip(*[elements[i:] for i in range(n)])


'''
def test_isCapitalized():
    s1 = "Ilike"
    s2 = "you"
    s3 = "II"
    s4 = "fI"

    print(s1, isCapitalized(s1))
    print(s2, isCapitalized(s2))
    print(s3, isCapitalized(s3))
    print(s4, isCapitalized(s4))


test_isCapitalized()
'''

'''
def test_regex():
    a = "I am zhang et al."
    b = "et al. et al ealsdfakl et al."
    c = "2.2.2. this is good"
    d = "3.2. a hat"

    print(subEtAl(a))
    print(subEtAl(b))
    print(subEtAl(c))
    print(subEtAl(d))

    print(subSectionIndex(a))
    print(subSectionIndex(b))
    print(subSectionIndex(c))
    print(subSectionIndex(d))


test_regex()
'''

'''
def test_wordSeparateSentence():
    test_1 = "zhang is afriend ofmine, and he likes,for instance, fish"
    test_2 = "differentialexpression is a hotsubject ofstudy."

    print(wordSeparateSentence(test_1))
    print(wordSeparateSentence(test_2))


test_wordSeparateSentence()
'''
