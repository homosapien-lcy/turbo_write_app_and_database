def checkAndAdd(dict, key, val):
    if key in dict:
        dict[key].append(val)
    else:
        dict[key] = [val]
