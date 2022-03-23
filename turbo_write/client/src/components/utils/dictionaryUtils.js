// convert an array to a map of element to index
export function arrToIndexMap(arr) {
  const index_map = {};
  arr.forEach((e, i) => {
    index_map[e] = i;
  });

  return index_map;
}

// a guarded function that first convert the lookup key to string
export function keysInclude(dictionary, lookup) {
  return Object.keys(dictionary).includes(lookup.toString());
}

// function for dictionary add
export function addOrAppend(dictionary, key, val) {
  // if already in, append, else, add to dictionary
  if (key in dictionary) {
    dictionary[key].push(val);
  } else {
    dictionary[key] = [val];
  }
}

// a method that sums up the values by key in dictionary box
export function dictionarySum(keys_to_sum, dictionary_box) {
  const sum_dictionary = {};
  // loop through keys
  keys_to_sum.forEach(k => {
    var sum = 0;
    // loop through dictionaries
    // cannot loop through values or entries
    // Object.values or Object.entries seem to
    // have problem when handling values of dictionary
    Object.keys(dictionary_box).forEach(part => {
      // retrieve dictionary by key
      const d = dictionary_box[part];
      // if this key is included in this d
      if (keysInclude(d, k)) {
        sum += d[k];
      }
    });
    sum_dictionary[k] = sum;
  });

  return sum_dictionary;
}

export function updateReferencesAndIndex(
  references,
  references_index,
  citation_count_sum
) {
  const r = references;
  const ri = references_index;

  Object.keys(citation_count_sum).forEach(index => {
    // get count value
    const num = citation_count_sum[index];

    // update references count
    r.reference_list[index].num = num;

    // update references index count
    const reference_text = r.reference_list[index].citation;
    ri[reference_text].num = num;
  });

  return [r, ri];
}

// sort an array of map by key field
export function sortByField(map_arr, key, ascending = true) {
  // for ascending, a - b
  if (ascending) {
    // [...] copy before sorting
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return a[key] - b[key];
    });
  } else {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return b[key] - a[key];
    });
  }

  return sorted_map_arr;
}

// sort an array of map by 2 key field
export function sortByTwoField(map_arr, key_1, key_2, ascending = true) {
  // for ascending, a - b
  if (ascending) {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return a[key_1] - b[key_1] || a[key_2] - b[key_2];
    });
  } else {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return b[key_1] - a[key_1] || b[key_2] - a[key_2];
    });
  }

  return sorted_map_arr;
}

// sort with a mix scoring function
export function sortByTwoFieldMixScore(
  map_arr,
  key_1,
  key_2,
  mix_fun,
  ascending = true
) {
  // for ascending, a - b
  if (ascending) {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return mix_fun(a[key_1], a[key_2]) - mix_fun(b[key_1], b[key_2]);
    });
  } else {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return mix_fun(b[key_1], b[key_2]) - mix_fun(a[key_1], a[key_2]);
    });
  }

  return sorted_map_arr;
}

// sort an array of map by 3 key field
export function sortByThreeField(
  map_arr,
  key_1,
  key_2,
  key_3,
  ascending = true
) {
  // for ascending, a - b
  if (ascending) {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return a[key_1] - b[key_1] || a[key_2] - b[key_2] || a[key_3] - b[key_3];
    });
  } else {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return b[key_1] - a[key_1] || b[key_2] - a[key_2] || b[key_3] - a[key_3];
    });
  }

  return sorted_map_arr;
}

// sort with a mix scoring function
export function sortByThreeFieldMixScore(
  map_arr,
  key_1,
  key_2,
  key_3,
  mix_fun,
  ascending = true
) {
  // for ascending, a - b
  if (ascending) {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return (
        mix_fun(a[key_1], a[key_2], a[key_3]) -
        mix_fun(b[key_1], b[key_2], b[key_3])
      );
    });
  } else {
    var sorted_map_arr = [...map_arr].sort(function(a, b) {
      return (
        mix_fun(b[key_1], b[key_2], b[key_3]) -
        mix_fun(a[key_1], a[key_2], a[key_3])
      );
    });
  }

  return sorted_map_arr;
}

// collect dictionaries by field
export function collectByField(map_arr, key) {
  var dictByField = {};
  for (var i = 0; i < map_arr.length; i++) {
    const cur_map = map_arr[i];
    // collect key value
    const key_val = cur_map[key];

    // push or initiate depends on existence
    addOrAppend(dictByField, key_val, cur_map);
  }

  return dictByField;
}

// merge arrays in a map
export function mergeMap(map_of_arr) {
  var merged_arr = [];
  Object.values(map_of_arr).forEach(function(arr) {
    merged_arr.push(...arr);
  });

  return merged_arr;
}

// remove redundant sentence groups
export function removeRedundant(arr, num_group) {
  // the sent_dist_cut should be num_group - 1 (parameter in the processor)
  const sent_dist_cut = num_group - 1;

  var filtered_arr = [];
  var last_collected_sent_id = -999;
  // loop through the array, and check each sent id
  for (var i = 0; i < arr.length; i++) {
    const cur_paper = arr[i];
    const cur_sent_id = cur_paper.sent_id;

    // if the id is less than sent_dist_cut away from the last id collected,
    // skip, otherwise, collect
    if (cur_sent_id - last_collected_sent_id > sent_dist_cut) {
      filtered_arr.push(cur_paper);
      last_collected_sent_id = cur_sent_id;
    }
  }

  return filtered_arr;
}

// remove redundant sentence groups in all arrs in a map
export function removeRedundantMap(map_of_arr, num_group) {
  var filtered_map_of_arr = {};

  Object.keys(map_of_arr).forEach(function(key) {
    filtered_map_of_arr[key] = removeRedundant(map_of_arr[key], num_group);
  });

  return filtered_map_of_arr;
}
