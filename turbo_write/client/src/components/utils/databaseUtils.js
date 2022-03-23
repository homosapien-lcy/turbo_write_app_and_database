import axios from "axios";
import { popText } from "./webpageUtils";

import {
  max_result_retrieve,
  query_len_to_num_group_map,
  max_query_len_for_lookup
} from "../constants/searchConstants";

import {
  sortByField,
  sortByTwoField,
  sortByThreeField,
  collectByField,
  removeRedundantMap,
  mergeMap
} from "./dictionaryUtils";

import { SERVER_ADDRESS } from "../constants/networkConstants";

// function use to generate const score search term
function const_score_search_generator(term) {
  return {
    constant_score: {
      filter: {
        match: {
          content: {
            query: term,
            // search results must include all terms
            //operator: "and"
            // fuzziness can actually cause inaccuracy sometimes
            fuzziness: "auto"
          }
        }
      }
    }
  };
}

function es_score_search_generator(term) {
  return {
    match: {
      content: {
        // since the user usually wants specific examples, thus
        // or query (default) that allow redundant terms works
        // more comfortably
        query: term,
        // search results must include all terms
        //operator: "and"
        // fuzziness can actually cause inaccuracy sometimes
        fuzziness: "auto"
      }
    }
  };
}

// filter for fields other than section
function field_filter_generator(field, term) {
  return {
    match: {
      [field]: {
        query: term,
        fuzziness: "auto"
      }
    }
  };
}

// filter for section
function section_filter_generator(part) {
  return { match: { section: part } };
}

export function removeRedundantWithNumGroup(search_results) {
  // get the num of group for filtering
  const num_group_for_filter = search_results[0].num_group;

  // sort by the sent_id field for next step
  const search_results_sorted_by_sent_id = sortByField(
    search_results,
    "sent_id"
  );

  // collect by document
  const search_results_sorted_by_sent_id_collected_by_doc_id = collectByField(
    search_results_sorted_by_sent_id,
    "doc_id"
  );

  // filter out the consecutive (redundant) sentence groups and merge into an array
  const filtered_search_results = mergeMap(
    removeRedundantMap(
      search_results_sorted_by_sent_id_collected_by_doc_id,
      num_group_for_filter
    )
  );

  return filtered_search_results;
}

// when multiple results has same doc_id and sent_id, only keep the
// ones with smallest num_group
// since already filtered by section during search, no need to worry about that
export function keepLowestGroupNumResults(search_results) {
  // sort
  const search_results_sorted_by_doc_id_sent_id_num_group = sortByThreeField(
    search_results,
    "doc_id",
    "sent_id",
    "num_group"
  );

  var lowestGroupNumResults = [];
  var last_doc_id = -9999;
  var last_sent_id = -9999;
  for (
    var i = 0;
    i < search_results_sorted_by_doc_id_sent_id_num_group.length;
    i++
  ) {
    const cur_search_result =
      search_results_sorted_by_doc_id_sent_id_num_group[i];
    const cur_doc_id = cur_search_result.doc_id;
    const cur_sent_id = cur_search_result.sent_id;

    // if the doc and sent id are the same, skip
    if (cur_doc_id == last_doc_id && cur_sent_id == last_sent_id) {
      continue;
    } else {
      lowestGroupNumResults.push(cur_search_result);
      last_doc_id = cur_doc_id;
      last_sent_id = cur_sent_id;
    }
  }

  return lowestGroupNumResults;
}

// remove redundant method for the search mix
export function removeRedundantSearchMix(search_results) {
  // collect the results by num_group
  // s_r_c_b_n_g = search_results_collected_by_num_group
  const s_r_c_b_n_g = collectByField(search_results, "num_group");

  // for each num group collection, apply removeRedundantWithNumGroup to remove redundance
  // s_r_c_b_n_g_r_r = search_results_collected_by_num_group_remove_redundant
  var s_r_c_b_n_g_r_r = {};
  Object.keys(s_r_c_b_n_g).forEach(k => {
    s_r_c_b_n_g_r_r[k] = removeRedundantWithNumGroup(s_r_c_b_n_g[k]);
  });

  // merge the results
  s_r_c_b_n_g_r_r = mergeMap(s_r_c_b_n_g_r_r);

  // apply keepLowestGroupNumResults
  const filtered_search_results = keepLowestGroupNumResults(s_r_c_b_n_g_r_r);

  return filtered_search_results;
}

/** old methods for search */
/* -------------------------------------------------------------------------------------------------------- */
/* the search with constant score (aka, hit or not) */
export async function search(
  collection_name,
  part,
  search_term,
  jounral_term,
  min_year,
  min_cited_times,
  min_sentence_length,
  search_generator
) {
  const quest = [];

  // const score search term
  // [part] evaluate part from object
  // and use value as key
  const search_term_settings = search_generator(search_term);

  const journal_term_settings = field_filter_generator("journal", jounral_term);

  const year_requirement = {
    range: {
      year: {
        gte: min_year
      }
    }
  };

  const cited_times_requirement = {
    range: {
      cited_times: {
        gte: min_cited_times
      }
    }
  };

  // length requirement
  const sent_length_requirement = {
    range: {
      number_of_words: {
        gte: min_sentence_length
      }
    }
  };

  const sort_by_score_and_cite_num = [
    {
      _score: {
        order: "desc"
      },
      cited_times: {
        order: "desc"
      }
    }
  ];

  // add both to quest
  quest.push(search_term_settings);

  // if journal term set, add to quest
  if (jounral_term.length > 0) {
    quest.push(journal_term_settings);
  }

  // if min year set, add to quest
  if (min_year.length > 0) {
    quest.push(year_requirement);
  }

  // if min cited times set, add to quest
  if (min_cited_times.length > 0) {
    quest.push(cited_times_requirement);
  }

  quest.push(sent_length_requirement);

  const section_filter = section_filter_generator(part);

  const response = await axios.post(`${SERVER_ADDRESS}/api/search`, {
    index: collection_name,

    // search and filter then by sent length
    body: {
      size: max_result_retrieve,
      query: {
        bool: {
          must: quest,
          filter: [section_filter]
        }
      },
      sort: sort_by_score_and_cite_num,
      highlight: {
        fields: {
          content: {}
        }
      }
    }
  });

  return response.data;
}

/* the search with constant score (aka, hit or not) */
export async function searchWithConstantScore(
  collection_name,
  part,
  search_term,
  jounral_term,
  min_year,
  min_cited_times,
  min_sentence_length
) {
  return await search(
    collection_name,
    part,
    search_term,
    jounral_term,
    min_year,
    min_cited_times,
    min_sentence_length,
    const_score_search_generator
  );
}

/* the search with elastic search score */
/* which works a little better */
export async function searchWithESScore(
  collection_name,
  part,
  search_term,
  jounral_term,
  min_year,
  min_cited_times,
  min_sentence_length
) {
  return await search(
    collection_name,
    part,
    search_term,
    jounral_term,
    min_year,
    min_cited_times,
    min_sentence_length,
    es_score_search_generator
  );
}

// get the document with doc_id and sent_id
export async function findSentence(collection_name, part, doc_id, sent_id) {
  const section_filter = section_filter_generator(part);

  const response = await axios.post(`${SERVER_ADDRESS}/api/search`, {
    index: collection_name,
    body: {
      query: {
        bool: {
          filter: [
            { term: { doc_id: doc_id } },
            { term: { sent_id: sent_id } },
            section_filter
          ]
        }
      }
    }
  });

  return response.data;
}

export async function findAndExtractSentence(
  collection_name,
  part,
  doc_id,
  sent_id
) {
  const response = await findSentence(collection_name, part, doc_id, sent_id);
  const number_of_hits = Number(response.hits.total.value);

  if (number_of_hits <= 0) {
    return "";
  } else {
    return response.hits.hits[0]._source.content;
  }
}

export async function findAllSentencesAndShow(collection_name, part, doc_id) {
  const section_filter = section_filter_generator(part);

  var response = await axios.post(`${SERVER_ADDRESS}/api/search`, {
    index: collection_name,
    // [part] evaluate part from object
    // and use value as key
    body: {
      size: 1000,
      sort: [{ sent_id: { order: "asc" } }],
      query: {
        bool: {
          filter: [{ term: { doc_id: doc_id } }, section_filter]
        }
      }
    }
  });

  response = response.data;

  const hits = response.hits.hits;
  const texts = hits.map(h => {
    return h._source.content;
  });

  const paragraph = texts.join(". ");

  popText(paragraph);
}
/* -------------------------------------------------------------------------------------------------------- */

/** new methods for search with mix group num */
/* -------------------------------------------------------------------------------------------------------- */
export async function searchMix(
  collection_name,
  part,
  search_term,
  jounral_term,
  min_year,
  min_cited_times,
  min_sentence_length,
  search_generator
) {
  const quest = [];

  // const score search term
  // [part] evaluate part from object
  // and use value as key
  const search_term_settings = search_generator(search_term);

  const journal_term_settings = field_filter_generator("journal", jounral_term);

  const year_requirement = {
    range: {
      year: {
        gte: min_year
      }
    }
  };

  const cited_times_requirement = {
    range: {
      cited_times: {
        gte: min_cited_times
      }
    }
  };

  // length requirement
  const sent_length_requirement = {
    range: {
      number_of_words: {
        gte: min_sentence_length
      }
    }
  };

  // num_group requirement
  // calculate # words in this query
  var query_length = search_term.split(" ").length;
  // set the query length to max if
  if (query_length > max_query_len_for_lookup) {
    query_length = max_query_len_for_lookup;
  }
  // num_group requirement, must be smaller than or equal to
  const num_group_requirement = {
    range: {
      num_group: {
        lte: query_len_to_num_group_map[query_length]
      }
    }
  };

  const sort_by_score_and_cite_num = [
    {
      _score: {
        order: "desc"
      },
      cited_times: {
        order: "desc"
      }
    }
  ];

  // add both to quest
  quest.push(search_term_settings);

  // if journal term set, add to quest
  if (jounral_term.length > 0) {
    quest.push(journal_term_settings);
  }

  // if min year set, add to quest
  if (min_year.length > 0) {
    quest.push(year_requirement);
  }

  // if min cited times set, add to quest
  if (min_cited_times.length > 0) {
    quest.push(cited_times_requirement);
  }

  quest.push(sent_length_requirement);

  quest.push(num_group_requirement);

  const section_filter = section_filter_generator(part);

  const response = await axios.post(`${SERVER_ADDRESS}/api/search`, {
    index: collection_name,

    // search and filter then by sent length
    body: {
      size: max_result_retrieve,
      query: {
        bool: {
          must: quest,
          filter: [section_filter]
        }
      },
      sort: sort_by_score_and_cite_num,
      highlight: {
        fields: {
          content: {}
        }
      }
    }
  });

  return response.data;
}

/* the search with constant score (aka, hit or not) */
export async function searchWithConstantScoreMix(
  collection_name,
  part,
  search_term,
  jounral_term,
  min_year,
  min_cited_times,
  min_sentence_length
) {
  return await searchMix(
    collection_name,
    part,
    search_term,
    jounral_term,
    min_year,
    min_cited_times,
    min_sentence_length,
    const_score_search_generator
  );
}

/* the search with elastic search score */
/* which works a little better */
export async function searchWithESScoreMix(
  collection_name,
  part,
  search_term,
  jounral_term,
  min_year,
  min_cited_times,
  min_sentence_length
) {
  return await searchMix(
    collection_name,
    part,
    search_term,
    jounral_term,
    min_year,
    min_cited_times,
    min_sentence_length,
    es_score_search_generator
  );
}

// get the document with doc_id, sent_id and num_group
export async function findSentenceMix(
  collection_name,
  part,
  doc_id,
  sent_id,
  num_group
) {
  const section_filter = section_filter_generator(part);

  const response = await axios.post(`${SERVER_ADDRESS}/api/search`, {
    index: collection_name,
    body: {
      query: {
        bool: {
          filter: [
            { term: { doc_id: doc_id } },
            { term: { sent_id: sent_id } },
            { term: { num_group: num_group } },
            section_filter
          ]
        }
      }
    }
  });

  return response.data;
}

export async function findAndExtractSentenceMix(
  collection_name,
  part,
  doc_id,
  sent_id,
  num_group
) {
  const response = await findSentenceMix(
    collection_name,
    part,
    doc_id,
    sent_id,
    num_group
  );
  const number_of_hits = Number(response.hits.total.value);

  if (number_of_hits <= 0) {
    return "";
  } else {
    return response.hits.hits[0]._source.content;
  }
}

export async function findAllSentencesAndShowMix(
  collection_name,
  part,
  doc_id,
  num_group
) {
  const section_filter = section_filter_generator(part);

  var response = await axios.post(`${SERVER_ADDRESS}/api/search`, {
    index: collection_name,
    // [part] evaluate part from object
    // and use value as key
    body: {
      size: 1000,
      sort: [{ sent_id: { order: "asc" } }],
      query: {
        bool: {
          filter: [
            { term: { doc_id: doc_id } },
            { term: { num_group: num_group } },
            section_filter
          ]
        }
      }
    }
  });

  response = response.data;

  const hits = response.hits.hits;
  const texts = hits.map(h => {
    return h._source.content;
  });

  const paragraph = texts.join(". ");

  popText(paragraph);
}

/* -------------------------------------------------------------------------------------------------------- */
