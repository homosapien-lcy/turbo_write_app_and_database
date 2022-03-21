import string

# count the number of digits in a string s


def countDigits(s):
    return sum(c.isdigit() for c in s)

# count number of punctuation in a string s


def countPunct(s):
    return sum((c in string.punctuation) for c in s)

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


'''
def test_isData():
    print('45e: ', isData('45e'))
    print('ge: ', isData('ge'))
    print('ewwe: ', isData('ewwe'))
    print('452: ', isData('452'))
    print('0.77: ', isData('0.77'))
    print('2e-20: ', isData('2e-20'))
    print('ddd: ', isData('ddd'))
    print('4e20: ', isData('4e20'))
    print('-99: ', isData('-99'))
    print('75%: ', isData('75%'))
    print('10: ', isData('10'))
    print('100: ', isData('100'))
    print('5: ', isData('5'))
    print('3: ', isData('3'))
    print('g: ', isData('g'))

test_isData()
'''
