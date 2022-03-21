import string

# count the number of digits in a string s


def countDigits(s):
    return sum(c.isdigit() for c in s)

# count number of punctuation in a string s


def countPunct(s):
    return sum((c in string.punctuation) for c in s)

# calculate the percent of certain characters


def percentCertainChar(s, countFunc):
    # remove spaces
    dried_string = ''.join(s.split())

    if len(dried_string) == 0:
        return 1
    return float(countFunc(dried_string)) / float(len(dried_string))


def percentDigits(s):
    return percentCertainChar(s, countDigits)


def percentPunct(s):
    return percentCertainChar(s, countPunct)
