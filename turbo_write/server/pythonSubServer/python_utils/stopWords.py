import string

from nltk.corpus import stopwords
stop_words_whole = set(stopwords.words('english'))
# a narrower set of stop words for only filter out a and the
determiners = set(["a", "an", "the"])

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# add single letters and digits to the stop words
letters_plus_digits = set(string.ascii_lowercase) | set(
    [str(i) for i in range(0, 10)])
ENGLISH_STOP_WORDS_plus_letters_plus_digits = ENGLISH_STOP_WORDS | letters_plus_digits
determiners_plus_letters_plus_digits = determiners | letters_plus_digits
