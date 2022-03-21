from collections import Counter

# convert counter's key to list


def counterToList(c):
    return list(c.keys())

# convert dict of counter to dict of list


def dictCounterToList(counter_dictionary):
    list_dict = {}
    for k in counter_dictionary.keys():
        list_dict[k] = counterToList(counter_dictionary[k])

    return list_dict


def combineCounter(counter_list):
    temp = Counter([])
    for i in range(0, len(counter_list)):
        temp += counter_list[i]

    return temp

# unify all counters (uni, bi, tri) into a single counter


def unifyDictCounter(counter_dictionary):
    temp = Counter([])
    for key in counter_dictionary.keys():
        temp += counter_dictionary[key]

    return temp

# merge multiple word_tables


def mergeDictionaryCounter(counter_dict_arr):
    key_set = set([])
    # collect all the keys
    for dictionary in counter_dict_arr:
        key_set = key_set | dictionary.keys()

    # merge dictionary of counters into 1 dictionary
    merge_dict_counter = {}
    for key in key_set:
        merge_dict_counter[key] = Counter([])

        for dictionary in counter_dict_arr:
            if key in dictionary.keys():
                merge_dict_counter[key] += dictionary[key]

    return merge_dict_counter


def counterToList(counter_table):
    counter_list = list(counter_table.items())
    return [x[0] for x in counter_list]


# only key the top top_cut of the grams


def keepTop(counter_table, top_cut):
    tops = counter_table.most_common(top_cut)
    temp = Counter([])
    for x, y in tops:
        temp[x] = y
    return temp

# for each element in the cut dictionary, only keep the tops


def keepTopInDictionary(counter_dictionary, cut_dictionary):
    temp = {}
    for key in cut_dictionary.keys():
        grams = counter_dictionary[key]
        cut = cut_dictionary[key]
        selected_grams = keepTop(grams, cut)
        temp[key] = selected_grams

    return temp
