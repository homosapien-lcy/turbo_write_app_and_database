import axios from "axios";
import { arrToIndexMap } from "../utils/dictionaryUtils";
import { sleeper } from "../utils/systemUtils";

import {
  segmentArticles,
  getArticleTitle,
  getAbstract,
  getDOI,
  getJournalInfos,
  getAuthorInfos
} from "../utils/textProcessingUtils";

export async function searchCitation(search_term) {
  const response = await axios.get(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
    {
      params: {
        db: "pubmed",
        term: search_term,
        sort: "relevance"
      }
    }
  );

  // get list of ids related to the search term
  var IDs = response.data.split("</Id>");
  IDs = IDs.map(ID => ID.split("<Id>")[1]);
  IDs = IDs.filter(ID => ID != undefined);

  /* using the ncbi api the right way! */
  var res = await axios.get(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
    {
      params: { db: "pubmed", id: IDs.join(","), retmode: "xml" }
    }
  );
  // 300 milisecond is the minimum timeout that will not cause
  // 429
  //.then(sleeper(300));

  res = await Promise.resolve(res.data);
  res = res.split("\n").join("");
  const res_segs = segmentArticles(res);
  const articleTitles = res_segs.map(seg => getArticleTitle(seg));
  const abstracts = res_segs.map(seg => getAbstract(seg));
  const DOIs = res_segs.map(seg => getDOI(seg));
  const citationPartJournal = res_segs.map(seg => getJournalInfos(seg));
  const citationPartAuthor = res_segs.map(seg => getAuthorInfos(seg));

  const paper_info = [];
  for (var i = 0; i < articleTitles.length; i++) {
    paper_info.push({
      title: articleTitles[i],
      abstract: abstracts[i],
      DOI: DOIs[i],
      link: "https://doi.org/" + DOIs[i],
      journal: citationPartJournal[i],
      author: citationPartAuthor[i]
    });
  }

  return paper_info;

  /* using the ncbi api the wrong way... */
  /*
  var paper_info = [];
  for (var i = 0; i < IDs.length; i++) {
    const ID = IDs[i];
    var res = await axios
      .get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", {
        params: { db: "pubmed", id: ID, retmode: "xml" }
      })
      // 300 milisecond is the minimum timeout that will not cause
      // 429
      .then(sleeper(300));

    res = await Promise.resolve(res.data);
    res = res.split("\n").join("");
    const articleTitle = getArticleTitle(res);
    const abstract = getAbstract(res);

    paper_info.push({
      title: articleTitle,
      abstract: abstract
    });
  }
  paper_info = await Promise.all(paper_info);
  */

  /* using the bionlp api */
  /*
  var paper_info = IDs.map(ID => {
    return axios.get(
      "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pubmed.cgi/BioC_json/" +
        ID +
        "/unicode"
    );
  });

  paper_info = await Promise.all(paper_info);
  paper_info = paper_info.map(info => info.data.documents[0].passages);
  paper_info = paper_info.map(info => {
    return {
      title: replaceUndefined(info[0]).text,
      abstract: replaceUndefined(info[1]).text
    };
  });
  */
}

export function splitByCitation(string) {
  // compile citation regex
  // () bracket around means: keep the split part after
  // splitting
  const citation_regex = new RegExp(/(\[[0-9]+\])/g);
  return string.split(citation_regex);
}

// check whether a string is a citation
export function isCitation(string) {
  // when initialize with 'g', the RegExp has states
  // and will cause alternating outputs, thus better restart
  // and not include 'g'
  const citation_regex = new RegExp(/(\[[0-9]+\])/);
  return citation_regex.test(string);
}

// generate a sorted list of references
export function sortedCitationsGen(text, references_lookup) {
  // order of sections to sort references
  const order = [
    "Abstract",
    "Introduction",
    "Methods",
    "Results",
    "Discussion",
    "Acknowledgement"
  ];

  var sorted_citations = [];
  order.forEach(section => {
    const section_text = text[section];
    // find citations
    var citations = section_text
      .replace(/\s\s+/g, " ")
      .match(/\[\s*&\s*(.*?)\s*&\s*\]/g);

    // if find any
    if (citations != null) {
      citations = citations.map(c => {
        // remove [ and ], remove space
        const clean_c = c
          .replace(/\[\s*&\s*/g, "")
          .replace(/\s*&\s*\]/g, "")
          .trim();

        // look up full reference
        return references_lookup[clean_c];
      });

      citations.forEach(citation => {
        // if not already added
        if (!sorted_citations.includes(citation)) {
          sorted_citations.push(citation);
        }
      });
    }
  });

  return sorted_citations;
}

export function processCitations(text, references, referencesLookup) {
  // generate map from ref to index
  const ref_index_map = arrToIndexMap(references);

  var ref_processed_text = {};
  Object.entries(text).forEach(([part_k, section_text]) => {
    var citations = section_text
      .replace(/\s\s+/g, " ")
      .match(/\[\s*&\s*(.*?)\s*&\s*\]/g);

    var ref_processed_text_k = section_text;
    // if any citation found, do the following
    if (citations != null) {
      citations = citations.map(citation_placeholder => {
        // remove [ and ], remove space
        const clean_c = citation_placeholder
          .replace(/\[\s*&\s*/g, "")
          .replace(/\s*&\s*\]/g, "")
          .trim();

        // get replace index from the map
        const replace_index =
          "[" + (ref_index_map[referencesLookup[clean_c]] + 1) + "]";
        // replace place holder with index
        ref_processed_text_k = ref_processed_text_k.replace(
          citation_placeholder,
          replace_index
        );
      });
    }

    ref_processed_text[part_k] = ref_processed_text_k;
  });
  return ref_processed_text;
}
