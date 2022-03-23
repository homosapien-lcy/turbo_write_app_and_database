from .tagAnalysisUtils import *

# check whether the noun segment contains a determiner
# and return it and the following word


def getDT(noun_segment):
    seg_len = len(noun_segment)
    for i in range(0, seg_len):
        w = noun_segment[i]
        # return the DT if contained
        if w[1] in ["DT", "PRP$"]:
            # if a DT is the end, means
            # it is not a DT for the real entity
            # of the sentence, should also skip
            # and let false return
            if (i+1) < seg_len:
                return (w[0], noun_segment[i+1][0])

    return False

# check and add determiner to the segment
# NM = nouns_mentioned
# NMITLS = nouns_mentioned_in_the_last_sentence


def checkAndAddDT(seg, NM, NMITLS):
    # if the segment is only 1 determiner, means
    # a sentence segmentation edge case,
    # return no suggestion
    if len(seg) == 1 and seg[0][1] == "DT":
        return None

    determiner = getDT(seg)
    # if determiner doesn't exist in the segment
    if not determiner:
        noun_in_seg = extractNoun(seg)
        # if the word is mentioned in previous sentence
        if noun_in_seg in NM:
            # check whether the word is singular
            is_singular = isSingular(noun_in_seg)
            # check whether the word is mentioned in
            # the previous sentence
            if noun_in_seg in NMITLS:
                # if yes, check singular or plural
                if is_singular:
                    return "this"
                else:
                    return "these"
            else:
                # else, use "the"
                return "the"
    # if determiner exist and is "a" or "an"
    # check whether the next pronunciation starts with vowel
    elif determiner[0] == "a":
        # if starts with vowel, should use "an"
        if startsWithVowel(determiner[1]):
            return "an"
    elif determiner[0] == "an":
        # if not start with vowel, should use "a"
        if not startsWithVowel(determiner[1]):
            return "a"

    return None

# suggest DT for a parsed sentence and return a
# list of nouns in this sentence


def suggestDT(parsed_sentence, NM, NMITLS):
    cur_nouns_mentioned = []
    suggestions = []
    for tree in parsed_sentence.subtrees():
        if tree.label() == "NP":
            # segment the leaves
            noun_segments = divideNPLeaves(tree.leaves())

            # extract nouns and add to mentioned
            cur_nouns_mentioned.extend(extractNounArr(noun_segments))

            for seg in noun_segments:
                # generate suggestions
                DT_suggestion = checkAndAddDT(
                    seg, NM, NMITLS)
                suggestions.append((parsed_sentence, seg, DT_suggestion))

    return suggestions, cur_nouns_mentioned

# method for DT suggestions for a whole array (an article)


def suggestDTArr(NP_parsed_sentences):
    nouns_mentioned = []
    nouns_mentioned_in_the_last_sentence = []

    all_suggestions = []

    for ps in NP_parsed_sentences:
        # generate suggestions and nouns mentioned in the current ps
        suggestions, cur_nouns_mentioned = suggestDT(
            ps, nouns_mentioned, nouns_mentioned_in_the_last_sentence)
        all_suggestions.extend(suggestions)

        # add to nouns mentioned
        nouns_mentioned_in_the_last_sentence = cur_nouns_mentioned
        nouns_mentioned.extend(cur_nouns_mentioned)

    return all_suggestions


'''
def test_getDT():
    sentences = [
        "biology watches a movie and sleep",
        "the man is very happy",
        "this man is very happy",
        "these men are very happy",
        "men are very happy",
        "those men are very happy",
        "those happy men"
    ]

    tagged_sentences = generateTagsArr(sentences)
    NP_parsed_sentences = parseSentences(tagged_sentences, findNP)

    for ps in NP_parsed_sentences:
        for tree in ps.subtrees():
            if tree.label() == "NP":
                # segment the leaves
                noun_segments = divideNPLeaves(tree.leaves())
                for seg in noun_segments:
                    print("seg: ", seg)
                    print(getDT(seg))


test_getDT()
'''
