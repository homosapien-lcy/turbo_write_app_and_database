import math from 'mathjs';

export function forEach(arr, f) {
  for (var i = 0, e = arr.length; i < e; ++i) f(arr[i]);
}

export function forAllProps(obj, callback) {
  if (!Object.getOwnPropertyNames || !Object.getPrototypeOf) {
    for (var name in obj) callback(name);
  } else {
    for (var o = obj; o; o = Object.getPrototypeOf(o)) Object.getOwnPropertyNames(o).forEach(callback);
  }
}

export function allPrevTokens(e, cur) {
  return e.getLineTokens(cur.line);
}

// function for getting unigram token
export function unigramToken(e, cur) {
  return e.getTokenAt(cur);
}

// each bigram has 3 tokens, including an operator or
// space in between
export function bigramToken(e, cur) {
  var token_list = e.getLineTokens(cur.line);
  var token_3 = token_list.pop();
  var token_2 = token_list.pop();
  var token_1 = token_list.pop();

  var temp_token = token_3;
  temp_token.end = token_3.end;
  temp_token.start = token_1.start;
  temp_token.state = token_3.state;
  temp_token.string = token_1.string + token_2.string + token_3.string;
  temp_token.type = token_3.type;

  return temp_token;
}

export function trigramToken(e, cur) {
  var token_list = e.getLineTokens(cur.line);
  var token_5 = token_list.pop();
  var token_4 = token_list.pop();
  var token_3 = token_list.pop();
  var token_2 = token_list.pop();
  var token_1 = token_list.pop();

  var temp_token = token_5;
  temp_token.end = token_5.end;
  temp_token.start = token_1.start;
  temp_token.state = token_5.state;
  temp_token.string = token_1.string + token_2.string + token_3.string + token_4.string + token_5.string;
  temp_token.type = token_5.type;

  return temp_token;
}

// join multiple array into one array
export function flattenArr(arr) {
  return [].concat.apply([], arr);
}

// get the leads for current word
export function getBiTriGramLeads(prevTokens) {
  // make a copy to keep the input intact
  var prevTokens_copy = prevTokens;

  // if no previous word, return empty
  if (prevTokens_copy.length <= 2) {
    return ['', ''];
  } else {
    var current = prevTokens_copy.pop();
    // remove empty space ' '
    prevTokens_copy.pop();
    var bi_lead = prevTokens_copy.pop();
    // return empty if no word as tri_lead
    if (prevTokens_copy.length <= 1) {
      return [bi_lead.string, ''];
    } else {
      prevTokens_copy.pop();
      var tri_lead = prevTokens_copy.pop();
      return [bi_lead.string, tri_lead.string + ' ' + bi_lead.string];
    }
  }
}

// search for freq of bi or trigram in the freq table
export function searchFreq(lead, word, freq_table) {
  // if empty, give score of 0
  if (!lead) {
    return 0;
  } else {
    const potential_gram = lead + ' ' + word;
    // if word not in table, give score of 0
    return freq_table[potential_gram] ? freq_table[potential_gram] : 0;
  }
}

// calculate frequency score using linear model
// in the order [uni, bi, tri]
export function freqScore(freq_vec, model_vec) {
  return math.dot(freq_vec, model_vec);
}

// rank the Phrases according to word frequency and context
export function rankPhrasesAndAddGrams(wordList, hintTokens, wordTable) {
  // handle the situation when nothing is loaded
  if (!wordTable) {
    return wordList;
  }

  const unigram_freq_table = wordTable[0];
  const bigram_freq_table = wordTable[1];
  const trigram_freq_table = wordTable[2];
  const bigram_lookup = wordTable[3];
  const trigram_lookup = wordTable[4];
  const model_dictionary = wordTable[5];

  // extract model
  const interpolation_model = [model_dictionary.unigram, model_dictionary.bigram, model_dictionary.trigram];

  const leads = getBiTriGramLeads(hintTokens);

  var sort_unigram = [];
  // new word list that contains uni, bi and tri
  for (var i = 0; i < wordList.length; i++) {
    const word = wordList[i];

    // getting leads (previous words)
    const bi_lead = leads[0];
    const tri_lead = leads[1];

    // extract frequencies
    const uni_freq = unigram_freq_table[word];
    const bi_freq = searchFreq(bi_lead, word, bigram_freq_table);
    const tri_freq = searchFreq(tri_lead, word, trigram_freq_table);

    const freq_vec = [uni_freq, bi_freq, tri_freq];

    // calculate and store frequency scores
    const freq_score = freqScore(freq_vec, interpolation_model);
    sort_unigram.push([word, freq_score]);
  }

  // sort words by score
  // b - a sort from big to small
  sort_unigram.sort(function(a, b) {
    return b[1] - a[1];
  });

  // take out the word
  sort_unigram = sort_unigram.map(x => x[0]);

  var sort_bigram = [];
  for (var i = 0; i < sort_unigram.length; i++) {
    const cur_unigram = sort_unigram[i];
    // then extract bi gram, sort by freq
    const sort_cur_bi_list = bigram_lookup[cur_unigram];

    // if don't have corresponding bigram, skip
    if (!sort_cur_bi_list) {
      continue;
    }

    sort_cur_bi_list.sort(function(a, b) {
      return b[2] - a[2];
    });

    sort_bigram.push(sort_cur_bi_list);
  }

  sort_bigram = flattenArr(sort_bigram);
  sort_bigram = sort_bigram.map(x => x[0]);

  var sort_trigram = [];
  for (var i = 0; i < sort_bigram.length; i++) {
    const cur_bigram = sort_bigram[i];

    // then extract tri gram, sort by freq
    const sort_cur_tri_list = trigram_lookup[cur_bigram];

    // if don't have corresponding trigram, skip
    if (!sort_cur_tri_list) {
      continue;
    }

    sort_cur_tri_list.sort(function(a, b) {
      return b[2] - a[2];
    });

    sort_trigram.push(sort_cur_tri_list);
  }

  sort_trigram = flattenArr(sort_trigram);
  sort_trigram = sort_trigram.map(x => x[0]);

  return flattenArr([sort_unigram, sort_bigram, sort_trigram]);
}
