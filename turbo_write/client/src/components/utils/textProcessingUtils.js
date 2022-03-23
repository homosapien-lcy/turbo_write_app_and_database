import {
  enw_key_map,
  ris_key_map,
  ris_priority_map
} from "../constants/citationFormattingConstants";

import { addOrAppend } from "../utils/dictionaryUtils";

/* general methods */
export function capFirstLetter(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// method for segmenting paragraphs
export function textToParagraph(text) {
  return text.split("\n");
}

// segment sentences and remove empty
export function segmentSentences(section) {
  var sentences = section.split(". ");
  sentences = sentences.filter(s => s.length > 0);
  return sentences;
}

// method for guarding undefined fields
export function replaceUndefinedAndNull(info) {
  if (info == undefined || info == null) {
    return [""];
  } else {
    return info;
  }
}

export function removeHTMLTags(text) {
  return text.replace(/<\/?(.*?)>/g, "");
}

export function removePunctuation(text) {
  return text.replace(/[~`!@#$%^&*(){}\[\];:"'<,.>?\/\\|_+=-]/g, "");
}

export function textToTokens(text) {
  // remove line breaks
  const one_line_text = text.split("\n").join(" ");
  // split by space
  const token_arr = one_line_text.split(" ");
  // filter empty
  // filter is not inplace, no need to copy, good!
  const non_empty_token_arr = token_arr.filter(t => {
    return t.length > 0;
  });
  return non_empty_token_arr;
}

// return a list of tokens from text
export function tokenize(text) {
  // remove tags
  const no_tag_text = removeHTMLTags(text);
  // remove punctuations
  const no_punct_text = removePunctuation(no_tag_text);
  // split text
  const token_arr = textToTokens(no_punct_text);
  return token_arr;
}

/* methods for bibText to citation */
// check and do a standard info extraction
export function bibTexCheckAndExtract(info) {
  return replaceUndefinedAndNull(info)[0]
    .replace(/(.*?)\s*=\s*{/g, "")
    .replace(/{/g, "")
    .replace(/},/g, "")
    .replace(/}/g, "")
    .trim();
}

export function findRegex(BT, item) {
  const re = new RegExp(item + "\\s*=\\s*{(.*?)},", "g");

  var found = BT.match(re);
  found = bibTexCheckAndExtract(found);

  return found;
}

export function bibTexToCitation(bibTex) {
  // remove blank spaces
  const BT = bibTex
    .trim()
    .split("\n")
    .join("");

  const author = findRegex(BT, "author");
  const title = findRegex(BT, "(,|\\s)title");
  const booktitle = findRegex(BT, "booktitle");
  const journal = findRegex(BT, "journal");
  const series = findRegex(BT, "series");
  const year = findRegex(BT, "year");
  const location = findRegex(BT, "location");
  const pages = findRegex(BT, "pages");
  const url = findRegex(BT, "url");

  // citation text
  var journal_text = "";

  // if not from a conference
  if (booktitle.length > 0) {
    journal_text += booktitle + ", ";
  } else if (journal.length > 0) {
    journal_text += journal + ", ";
  } else {
    journal_text += series + ", ";
  }

  journal_text += pages + ", ";
  journal_text += location + ", ";
  journal_text += year;

  // format it
  const citation_text = generateCitation(
    author + ".",
    title + ".",
    journal_text
  );

  // short citation text: authors + year + title (part)
  var short_citation_text = generateShortCitation(author, year, title);

  // format it
  short_citation_text = short_citation_text.replace(/\s\s+/g, " ").trim();

  const citation_info = {
    citation: citation_text,
    citation_short: short_citation_text,
    title: title,
    author: author,
    journal: journal.length != 0 ? journal : booktitle,
    link: url
  };

  return citation_info;
}

// common citation and short citation generator for enw and ris
export function citationAndShortGeneratorEnwRisCommon(content_dict) {
  // default in case of error
  var citation_info = {
    citation: "",
    citation_short: "",
    title: "",
    author: "",
    journal: "",
    link: "https://doi.org/"
  };

  try {
    var { title, author, journal, volume, issue, page, year } = content_dict;

    // join array into text
    title = title.join(", ");
    author = author.join(", ");
    journal = journal.join(", ");
    volume = volume.join(", ");
    issue = issue.join(", ");
    page = page.join(", ");
    year = year.join(", ");

    // generate full citation
    const journal_text = generateJournalText({
      journal: journal,
      abbrev: journal,
      year: year,
      volume: volume,
      issue: issue,
      page: page
    });

    const citation_text = generateCitation(
      author + ".",
      title + ".",
      journal_text
    );

    // generate short citation
    var short_citation_text = generateShortCitation(author, year, title);

    // format it
    short_citation_text = short_citation_text.replace(/\s\s+/g, " ").trim();

    citation_info = {
      citation: citation_text,
      citation_short: short_citation_text,
      title: title,
      author: author,
      journal: journal,
      link: "https://doi.org/"
    };
  } catch (err) {
    console.log(err);
    // if something wrong, alert and return empty default dictionary
    alert("输入内容格式不正确或内容不标准，请检查");
  }

  return citation_info;
}

// convert enw to citation
export function enwToCitation(enw) {
  // remove blank spaces
  const clean_enw = enw.trim();
  const content_arr = clean_enw.split("\n");

  const content_dict = {};

  content_arr.forEach(content => {
    const split_line = content.trim().split(" ");
    const key = split_line[0];
    // if key in encoded
    if (key in enw_key_map) {
      const common_key = enw_key_map[key];
      addOrAppend(content_dict, common_key, split_line.slice(1).join(" "));
    }
  });

  const citation_info = citationAndShortGeneratorEnwRisCommon(content_dict);

  return citation_info;
}

export function risToCitation(ris) {
  const clean_ris = ris.trim();
  const content_arr = clean_ris.split("\n");

  const content_dict = {};
  // dictionary to save the priority that already saved
  const max_priority_dict = {};
  content_arr.forEach(content => {
    const split_line = content.trim().split(" - ");
    const key = split_line[0].trim();

    // if key in encoded
    if (key in ris_key_map) {
      const common_key = ris_key_map[key];
      const cur_priority = ris_priority_map[key];

      // whether max priority saved
      if (common_key in max_priority_dict) {
        // if larger, set max priority
        if (cur_priority > max_priority_dict[common_key]) {
          // need to save with common_key
          max_priority_dict[common_key] = cur_priority;
        }
      } else {
        // else set it
        max_priority_dict[common_key] = cur_priority;
      }

      addOrAppend(content_dict, common_key, [
        split_line[1].trim(),
        cur_priority
      ]);
    }
  });

  // filter the dictionary with max priority
  const max_priority_filtered_content_dict = {};
  Object.keys(content_dict).forEach(k => {
    const max_priority = max_priority_dict[k];
    const content = content_dict[k];
    const filtered_content = [];
    // loop through contents
    content.forEach(ele => {
      // ele[0] is content, ele[1] is priority
      if (ele[1] < max_priority) {
        // for forEach loop, return functions like continue
        return;
      }

      filtered_content.push(ele[0]);
    });

    max_priority_filtered_content_dict[k] = filtered_content;
  });

  // process start and end page
  var start_page = "";
  var end_page = "";
  if ("start_page" in max_priority_filtered_content_dict) {
    start_page = max_priority_filtered_content_dict.start_page;
  }
  if ("end_page" in max_priority_filtered_content_dict) {
    end_page = max_priority_filtered_content_dict.end_page;
  }
  max_priority_filtered_content_dict.page = [start_page + "-" + end_page];

  const citation_info = citationAndShortGeneratorEnwRisCommon(
    max_priority_filtered_content_dict
  );

  return citation_info;
}

/* methods for ncbi message to citation */
// check and do a standard info extraction
export function ncbiCheckAndExtract(info) {
  return replaceUndefinedAndNull(info)[0]
    .replace(/<\/?(.*?)>/g, "")
    .trim();
}

// segment ncbi message by articles
export function segmentArticles(xml_text) {
  // add (.*?) in between to include PubmedArticle and PubmedBookArticle
  var segments = xml_text.match(
    /<Pubmed(.*?)Article>(.*?)<\/Pubmed(.*?)Article>/g
  );
  segments = replaceUndefinedAndNull(segments);
  return segments.map(function(val) {
    return val.replace(/<\/?Pubmed(.*?)Article>/g, "");
  });
}

// a method that acquires DOI from the link
export function getDOI(xml_text) {
  // match PubmedArticle other than DOI, since corrections can contain more than 1 DOI
  // and we only need the first one
  var DOIs = xml_text.match(
    /<ELocationID EIdType="doi"(.*?)>(.*?)<\/ELocationID>/g
  );
  DOIs = replaceUndefinedAndNull(DOIs);
  DOIs = DOIs.map(function(val) {
    return val.replace(/<\/?ELocationID(.*?)>/g, "");
  });
  // only return the first element which is the DOI
  return DOIs[0];
}

export function getArticleTitle(xml_text) {
  var titles = xml_text.match(/<ArticleTitle(.*?)>(.*?)<\/ArticleTitle>/g);
  titles = replaceUndefinedAndNull(titles);
  titles = titles.map(function(val) {
    var title = val.replace(/<\/?ArticleTitle(.*?)>/g, "");
    // replace ">" and "<" signs
    title = title.replace(/&gt;/g, ">");
    title = title.replace(/&lt;/g, "<");
    title = title.replace(/&quot;/g, '"');

    // if title doesn't end with "." and is not empty add it
    if (title.slice(-1) != "." && title.trim().length != 0) {
      title = title + ".";
    }

    return title;
  });
  // only return the first element which is the title
  return titles[0];
}

export function getAbstract(xml_text) {
  var abstracts = xml_text.match(/<Abstract>(.*?)<\/Abstract>/g);
  abstracts = replaceUndefinedAndNull(abstracts);
  abstracts = abstracts.map(function(val) {
    // replace all <> in the sentences
    return val.replace(/<\/?(.*?)>/g, "");
  });

  // preprocess output
  abstracts = abstracts.join(" \n");
  // remove unwanted spaces
  abstracts = abstracts.split(" ");
  abstracts = abstracts.filter(seg => seg.length > 0);
  abstracts = abstracts.join(" ");

  return abstracts;
}

export function getJournalInfos(xml_text) {
  // extract the journal and article info
  // for the other infos and pages
  var journalInfos = xml_text.match(/<Journal>(.*?)<\/Journal>/g);
  var articleInfos = xml_text.match(/<Article(.*?)>(.*?)<\/Article>/g);
  var bookInfos = xml_text.match(/<Book(.*?)>(.*?)<\/Book>/g);

  journalInfos = replaceUndefinedAndNull(journalInfos);
  articleInfos = replaceUndefinedAndNull(articleInfos);
  bookInfos = replaceUndefinedAndNull(bookInfos);

  var citationPartJournal = [];
  for (var i = 0; i < journalInfos.length; i++) {
    const JI = journalInfos[i];
    const AI = articleInfos[i];
    const BI = bookInfos[i];

    // if both info doesn't exist, process as book
    if (JI.length == 0 && AI.length == 0) {
      var bookTitle = BI.match(/<BookTitle(.*?)>(.*?)<\/BookTitle>/g);
      bookTitle = ncbiCheckAndExtract(bookTitle);
      var year = BI.match(/<PubDate>(.*?)<\/PubDate>/g);
      year = ncbiCheckAndExtract(year);
      var publisherName = BI.match(/<PublisherName>(.*?)<\/PublisherName>/g);
      publisherName = ncbiCheckAndExtract(publisherName);
      var publisherLocation = BI.match(
        /<PublisherLocation>(.*?)<\/PublisherLocation>/g
      );
      publisherLocation = ncbiCheckAndExtract(publisherLocation);

      // book info in dictionary text format
      const bookBox = {
        book: bookTitle,
        year: year,
        publisher: publisherName,
        Location: publisherLocation
      };

      // book info in text format
      var bookText = "";
      bookText += bookTitle + ", ";

      if (publisherName.length != 0) {
        bookText += publisherName + ", ";
      }

      if (publisherLocation.length != 0) {
        bookText += publisherLocation + ", ";
      }

      bookText += year + ";";

      bookText = bookText.trim();

      citationPartJournal.push({
        journal: bookText,
        journalInfo: bookBox
      });
    }
    // else process as journal
    else {
      // extract all infos
      var year = JI.match(/<Year>(.*?)<\/Year>/g);
      year = ncbiCheckAndExtract(year);
      var volume = JI.match(/<Volume>(.*?)<\/Volume>/g);
      volume = ncbiCheckAndExtract(volume);
      var issue = JI.match(/<Issue>(.*?)<\/Issue>/g);
      issue = ncbiCheckAndExtract(issue);
      var journalTitle = JI.match(/<Title>(.*?)<\/Title>/g);
      journalTitle = ncbiCheckAndExtract(journalTitle);
      var journalTitleAbbrev = JI.match(
        /<ISOAbbreviation>(.*?)<\/ISOAbbreviation>/g
      );
      journalTitleAbbrev = ncbiCheckAndExtract(journalTitleAbbrev);
      var pageInfo = AI.match(/<Pagination(.*?)>(.*?)<\/Pagination>/g);
      pageInfo = ncbiCheckAndExtract(pageInfo);

      // journal info in dictionary text format
      const journalBox = {
        journal: journalTitle,
        abbrev: journalTitleAbbrev,
        year: year,
        volume: volume,
        issue: issue,
        page: pageInfo
      };

      const journalText = generateJournalText(journalBox);

      citationPartJournal.push({
        journal: journalText,
        journalInfo: journalBox
      });
    }
  }

  // only return the first element which is the journal info
  return citationPartJournal[0];
}

export function getAuthorInfos(xml_text) {
  var authorInfos = xml_text.match(/<AuthorList(.*?)>(.*?)<\/AuthorList>/g);
  authorInfos = replaceUndefinedAndNull(authorInfos);

  authorInfos = authorInfos.map(authorInfo => {
    var authorList = authorInfo.match(/<Author(.*?)>(.*?)<\/Author>/g);
    // guard the author list
    authorList = replaceUndefinedAndNull(authorList);

    var authorsBox = [];
    var authorsText = "";
    var authorsTextShort = "";
    var type = [];

    for (var i = 0; i < authorList.length; i++) {
      const authorProfile = authorList[i];

      // get all parts of an author name
      var lastName = authorProfile.match(/<LastName>(.*?)<\/LastName>/g);
      lastName = ncbiCheckAndExtract(lastName).trim();
      // capitalized the first letter
      lastName = capFirstLetter(lastName);
      var firstName = authorProfile.match(/<ForeName>(.*?)<\/ForeName>/g);
      firstName = ncbiCheckAndExtract(firstName).trim();
      var abbrevFirstName = authorProfile.match(/<Initials>(.*?)<\/Initials>/g);
      abbrevFirstName = ncbiCheckAndExtract(abbrevFirstName).trim();

      // if two fields are empty, means the case of collective name
      if (lastName.length == 0 && abbrevFirstName.length == 0) {
        type.push("organization");

        // extract collective name
        var collectiveName = authorProfile.match(
          /<CollectiveName>(.*?)<\/CollectiveName>/g
        );
        collectiveName = ncbiCheckAndExtract(collectiveName).trim();
        // add dictionary style
        authorsBox.push({
          lastName: collectiveName,
          firstName: "",
          abbrevFirstName: ""
        });

        // add "." at the end
        authorsText += collectiveName + ", ";
      }
      // if the names are in normal format
      else {
        type.push("person");

        // name in dictionary style
        authorsBox.push({
          lastName: lastName,
          firstName: firstName,
          abbrevFirstName: abbrevFirstName
        });

        // name in citation text style
        authorsText += lastName + " ";
        authorsText += abbrevFirstName + ", ";
      }
    }

    // replace the last ", " with ".", also remove space on the two sides
    authorsText = (authorsText.slice(0, -2) + ".").trim();

    if (authorsBox.length > 1) {
      authorsTextShort = authorsBox[0].lastName + " et al.";
    } else {
      authorsTextShort = authorsBox[0].lastName + ".";
    }

    return {
      type: type,
      authors: authorsText,
      authorsList: authorsBox,
      authorsTextShort: authorsTextShort
    };
  });

  // only return the first element which is the authorinfo
  return authorInfos[0];
}

export function endNoteToCitations(endnote_text) {
  // sometimes, the empty spaces on the two ends can cause
  // bug, thus trim
  var endnote_info = endnote_text.trim().split("\n\n");
  endnote_info = endnote_info.slice(1);
  endnote_info = endnote_info.map(info => {
    return info.split("\n");
  });

  const paper_info = endnote_info.map(info => {
    const citation_text = info[0].trim();
    const title = citation_text
      .match(/"(.*?)"/g)[0]
      .replace(/"/g, "")
      .slice(0, -1);
    // match XXXXXX(year)
    const author_and_year = citation_text.match(/(.*?)\((19|20)[0-9]{2}\)/g)[0];
    const author_and_year_segs = author_and_year.split("(");
    var authorText = author_and_year_segs[0].trim();

    if (authorText.slice(-1) != ".") {
      authorText += ".";
    }

    const year = author_and_year_segs[1].slice(0, -1);

    const journal = citation_text
      .match(/"\s(.*?)\:(.*?)\./g)[0]
      .slice(1)
      .trim();
    const pageInfo = journal.match(/\d{1,}-\d{1,}/g)[0];
    const issue = journal.match(/\(\d{1,}\)/g)[0].replace(/(\(|\))/g, "");
    const volume = journal.match(/\d{1,}\(/g)[0].slice(0, -1);
    const journalTitleWithIssueAndVolume = journal.split(":")[0];
    const journalTitle = journalTitleWithIssueAndVolume
      .replace(/\d{1,}(\(\d{1,}\))/g, "")
      .trim();
    const journalTitleAbbrev = journalTitle;

    const abstract = info
      .slice(1)
      .join("\n")
      .trim();

    const journalBox = {
      journal: journalTitle,
      abbrev: journalTitleAbbrev,
      year: year,
      volume: volume,
      issue: issue,
      page: pageInfo
    };

    const journalText = generateJournalText(journalBox);

    return {
      title: title,
      abstract: abstract,
      DOI: "",
      link: "https://doi.org/",
      journal: {
        journal: journalText,
        journalInfo: journalBox
      },
      author: {
        type: [],
        authors: authorText,
        authorsList: [],
        authorsTextShort: authorText
      },
      citation: citation_text
    };
  });

  return paper_info;
}

/* methods for citation generation */
export function generateCitation(authors, title, journal) {
  return (authors + " " + title + " " + journal).replace(/\s\s+/g, " ").trim();
}

// old function
/*
export function generateShortCitation(authorsTextShort, journal) {
  return (authorsTextShort + " " + journal).replace(/\s\s+/g, " ").trim();
}
*/

// generate short citation as mark in the paper
export function generateShortCitation(authorsTextShort, year, title) {
  const take_first_n_name_char = 7;
  const take_first_n_title_char = 10;

  return (
    authorsTextShort.slice(0, take_first_n_name_char) +
    ", " +
    year +
    ", " +
    title.slice(0, take_first_n_title_char)
  )
    .replace(/\s\s+/g, " ")
    .trim();
}

export function generateJournalText(journalBox) {
  const { journal, abbrev, year, volume, issue, page } = journalBox;

  // journal info in citation text format
  var journalText = "";
  // add title and year
  // the abbrev already has "." at the end,
  // no extra "." needed
  journalText += abbrev + " ";
  journalText += year + ";";
  // add optional items: volume, issue, page
  if (volume.length != 0) {
    journalText += volume;
  }
  if (issue.length != 0) {
    journalText += "(" + issue + ")";
  }
  if (page.length != 0) {
    journalText += ":" + page + ".";
  }

  // remove the space on the two sides
  journalText = journalText.trim();

  return journalText;
}

// convert highligh arr to highlight text
export function toHighlightText(highlight) {
  return "... " + highlight.join(" ... ") + " ...";
}
