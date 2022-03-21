import string
import re


def removeChar(s, char):
    return ''.join(s.split(char))


def removeSpace(s):
    return removeChar(s, ' ')


def removeNull(s):
    return removeChar(s, '\x00')


def removeDigit(s):
    return re.sub(r'[0-9]+', '', s)

# substitute punctuation with space


def subPunct(s):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    return regex.sub(' ', s)

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
