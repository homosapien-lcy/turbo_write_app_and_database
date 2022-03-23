import React, { Component } from "react";
import { Col, Row, Input, Button, Select } from "antd";

import ExpandableText from "../common_components/expandableText";

import {
  ESScoreDecayRefNum,
  ESScoreDecayRefNumMultDecayHit
} from "../../utils/scoringUtils";

import {
  searchWithConstantScoreMix,
  searchWithESScoreMix,
  findAndExtractSentenceMix,
  findAllSentencesAndShowMix,
  removeRedundantWithNumGroup,
  removeRedundantSearchMix
} from "../../utils/databaseUtils";
/*
import {
  searchWithConstantScore,
  searchWithESScore,
  findAndExtractSentence,
  findAllSentencesAndShow
} from "../../utils/databaseUtils";
*/

import {
  sentLengthFilterOpt,
  databaseOpt
} from "../../constants/optionConstants";

import { toHighlightText, tokenize } from "../../utils/textProcessingUtils";

import {
  sortByTwoField,
  sortByTwoFieldMixScore,
  sortByThreeFieldMixScore
} from "../../utils/dictionaryUtils";

const InputGroup = Input.Group;
const Option = Select.Option;

class ExamplePanel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // requirement for journal name
      journal_name_must: "",
      // limit journals to be after year_limit
      year_limit: "",
      cited_times_limit: "",
      searchable_parts: ["Introduction", "Methods", "Results", "Discussion"],
      collection_name: databaseOpt[0],
      size_filter: sentLengthFilterOpt[1],
      expand: {},
      show_advance_filters: false,
      loading: false
    };

    // initialize expand
    for (var i = 0; i < this.props.search_results.length; i++) {
      this.state.expand[i] = false;
    }
  }

  showAdvance = e => {
    this.setState({ show_advance_filters: true });
  };

  hideAdvance = e => {
    this.setState({ show_advance_filters: false });
  };

  setSearchJournal = e => {
    this.setState({ journal_name_must: e.target.value });
  };

  setSearchYear = e => {
    this.setState({ year_limit: e.target.value });
  };

  setSearchCitedTimes = e => {
    this.setState({ cited_times_limit: e.target.value });
  };

  handleDatabaseChange = value => {
    this.setState({
      collection_name: value
    });
  };

  handleSizeFilterChange = value => {
    this.setState({
      size_filter: value
    });
  };

  onSearchSubmit = async () => {
    const part = this.props.part;

    // check whether the section has examples
    if (!this.state.searchable_parts.includes(part)) {
      alert(
        "此部分没有例句，请选择Introduction, Methods, Results, Discussion部分之后再进行搜索"
      );
      return;
    }

    this.setState({ loading: true });

    // search
    const response = await searchWithESScoreMix(
      this.state.collection_name,
      part,
      // remove spaces from two sides
      this.props.search_term.trim(),
      this.state.journal_name_must.trim(),
      this.state.year_limit.trim(),
      this.state.cited_times_limit.trim(),
      this.state.size_filter
    );
    /*
    const response = await searchWithESScore(
      this.state.collection_name,
      part,
      // remove spaces from two sides
      this.props.search_term.trim(),
      this.state.journal_name_must.trim(),
      this.state.year_limit.trim(),
      this.state.cited_times_limit.trim(),
      this.state.size_filter
    );
    */

    const hits_arr = response.hits.hits;
    var search_results = [];

    // if anything found
    if (hits_arr.length > 0) {
      // await only wait for 1 promise,
      // for waiting an array of promise,
      // need to put promise.all before it
      search_results = await Promise.all(
        hits_arr.map(async h => {
          const score = Number(h._score);

          // collect sentence info
          const title = h._source.title;
          const journal = h._source.journal;
          const year = Number(h._source.year);
          const cited_times = Number(h._source.cited_times);
          const num_group = Number(h._source.num_group);

          // collect doc and sent id
          const cur_doc_id = Number(h._source.doc_id);
          const cur_sent_id = Number(h._source.sent_id);

          const cur_sent = h._source.content;

          // calculate the number of words hit
          const cur_sent_tokens = tokenize(cur_sent);
          const search_term_tokens = tokenize(this.props.search_term);
          // intersect the two sets
          const cur_sent_tokens_set = new Set(cur_sent_tokens);
          const search_term_tokens_set = new Set(search_term_tokens);
          // intersect the two sets
          // here, use ... to expand the set into array, since set
          // doesn't have filter function
          const unique_hits = [...search_term_tokens_set].filter(t =>
            cur_sent_tokens_set.has(t)
          );
          // get number of token hits
          const cur_num_query_word_hit = unique_hits.size;
          const cur_percent_query_word_hit =
            cur_num_query_word_hit / search_term_tokens.length;

          // add highlight
          const cur_sent_marked = "<em><u>" + cur_sent + "</u></em>";
          const highlight = h.highlight.content;

          const prev_sent_id = cur_sent_id - 1;
          const next_sent_id = cur_sent_id + 1;

          const prev_sent = await findAndExtractSentenceMix(
            this.state.collection_name,
            part,
            cur_doc_id,
            prev_sent_id,
            num_group
          );
          /*
          const prev_sent = await findAndExtractSentence(
            this.state.collection_name,
            part,
            cur_doc_id,
            prev_sent_id
          );
          */

          const next_sent = await findAndExtractSentenceMix(
            this.state.collection_name,
            part,
            cur_doc_id,
            next_sent_id,
            num_group
          );
          /*
          const next_sent = await findAndExtractSentence(
            this.state.collection_name,
            part,
            cur_doc_id,
            next_sent_id
          );
          */

          return {
            score: score,
            num_query_word_hit: cur_num_query_word_hit,
            percent_query_word_hit: cur_percent_query_word_hit,
            num_group: num_group,
            title: title,
            journal: journal,
            year: year,
            doc_id: cur_doc_id,
            sent_id: cur_sent_id,
            hit_text: [prev_sent, cur_sent, next_sent],
            // the /uXXXX codes have already
            // being converted to symbols in response
            hit_text_marked: [prev_sent, cur_sent_marked, next_sent],
            cited_times: cited_times,
            abbrev_text: cur_sent_marked
          };
        })
      );
    } else {
      // else, return an empty result with -1
      // to indicate not found
      search_results = [
        {
          score: -1,
          // no need for word hit number
          // set to 0
          num_query_word_hit: 0,
          percent_query_word_hit: 0,
          num_group: 0,
          title: "No result found",
          journal: "",
          year: -1,
          doc_id: -1,
          sent_id: -1,
          hit_text: [],
          // the /uXXXX codes have already
          // being converted to symbols in response
          hit_text_marked: [],
          cited_times: -1,
          abbrev_text: ""
        }
      ];
    }

    const filtered_search_results = removeRedundantSearchMix(search_results);

    // sort by a mix score function of citation, score and percent hit
    // lambda function for score calculation
    const ESScore_1_LogRefNum_0_1_SqrtHit = function(
      es_score,
      cited_times,
      percent_hit
    ) {
      return ESScoreDecayRefNumMultDecayHit(
        1,
        es_score,
        0.1,
        Math.log,
        cited_times,
        Math.sqrt,
        percent_hit
      );
    };
    const sorted_filtered_search_results = sortByThreeFieldMixScore(
      filtered_search_results,
      "score",
      "cited_times",
      "percent_query_word_hit",
      ESScore_1_LogRefNum_0_1_SqrtHit,
      false
    );

    /*
    // sort by a mix score function of citation and score
    // lambda function for score calculation
    const ESScore_1_LogRefNum_0_1 = function(es_score, cited_times) {
      return ESScoreDecayRefNum(1, es_score, 0.1, Math.log, cited_times);
    };
    const sorted_filtered_search_results = sortByTwoFieldMixScore(
      filtered_search_results,
      "score",
      "cited_times",
      ESScore_1_LogRefNum_0_1,
      false
    );
    */

    /*
    // sort by citation and then by score (same order as in the search)
    const sorted_filtered_search_results = sortByTwoField(
      filtered_search_results,
      "cited_times",
      "score",
      false
    );
    */

    this.props.setSearchResults(sorted_filtered_search_results);
    //this.props.setSearchResults(search_results);

    // change the loading state
    this.setState({ loading: false });
  };

  navigateSentence = async (i, change) => {
    const part = this.props.part;
    const search_results = this.props.search_results;

    var search_result_i = search_results[i];
    const { doc_id, sent_id } = search_result_i;

    const cur_title = search_result_i.title;
    const cur_journal = search_result_i.journal;
    // already numbers when coming out of search_result_i, no need
    // to convert
    const cur_year = search_result_i.year;
    const cur_cited_times = search_result_i.cited_times;
    const cur_num_group = search_result_i.num_group;

    const cur_doc_id = doc_id;
    const cur_sent_id = sent_id + change;
    const prev_sent_id = cur_sent_id - 1;
    const next_sent_id = cur_sent_id + 1;

    var cur_sent = await findAndExtractSentenceMix(
      this.state.collection_name,
      part,
      cur_doc_id,
      cur_sent_id,
      cur_num_group
    );
    /*
    var cur_sent = await findAndExtractSentence(
      this.state.collection_name,
      part,
      cur_doc_id,
      cur_sent_id
    );
    */

    // add highlight
    const cur_sent_marked = "<em><u>" + cur_sent + "</u></em>";

    const prev_sent = await findAndExtractSentenceMix(
      this.state.collection_name,
      part,
      cur_doc_id,
      prev_sent_id,
      cur_num_group
    );
    /*
    const prev_sent = await findAndExtractSentence(
      this.state.collection_name,
      part,
      cur_doc_id,
      prev_sent_id
    );
    */

    const next_sent = await findAndExtractSentenceMix(
      this.state.collection_name,
      part,
      cur_doc_id,
      next_sent_id,
      cur_num_group
    );
    /*
    const next_sent = await findAndExtractSentence(
      this.state.collection_name,
      part,
      cur_doc_id,
      next_sent_id
    );
    */

    search_results[i] = {
      score: 0,
      // no need for word hit number
      // set to 0
      num_query_word_hit: 0,
      percent_query_word_hit: 0,
      num_group: cur_num_group,
      title: cur_title,
      journal: cur_journal,
      year: cur_year,
      doc_id: cur_doc_id,
      sent_id: cur_sent_id,
      hit_text: [prev_sent, cur_sent, next_sent],
      // the /uXXXX codes have already
      // being converted to symbols in response
      hit_text_marked: [prev_sent, cur_sent_marked, next_sent],
      cited_times: cur_cited_times,
      abbrev_text: cur_sent_marked
    };

    this.setState({ search_results: search_results });
  };

  viewFull = async i => {
    const part = this.props.part;
    const search_results = this.props.search_results;

    var search_result_i = search_results[i];
    const { doc_id, sent_id, num_group } = search_result_i;

    findAllSentencesAndShowMix(
      this.state.collection_name,
      part,
      doc_id,
      num_group
    );
    //findAllSentencesAndShow(this.state.collection_name, part, doc_id);
  };

  renderAdvanceFilters() {
    if (this.state.show_advance_filters) {
      return (
        <div>
          <Select
            size="small"
            placeholder="选择文章学科"
            style={{ width: 142, margin: "5px 0px" }}
            onChange={this.handleDatabaseChange}
          >
            {databaseOpt.map(DB => (
              <Option key={DB}>{DB}</Option>
            ))}
          </Select>
          <Select
            size="small"
            placeholder="句子长度过滤"
            style={{ width: 142, margin: "5px 5px" }}
            onChange={this.handleSizeFilterChange}
          >
            {sentLengthFilterOpt.map(sLength => (
              <Option key={sLength}>{sLength}</Option>
            ))}
          </Select>
          <InputGroup>
            <Col span={13}>
              <Input
                size="small"
                placeholder="期刊名称过滤"
                value={this.state.journal_name_must}
                onChange={this.setSearchJournal}
                onPressEnter={this.onSearchSubmit}
              />
            </Col>
            <Col span={5}>
              <Input
                size="small"
                placeholder="年份"
                value={this.state.year_limit}
                onChange={this.setSearchYear}
                onPressEnter={this.onSearchSubmit}
              />
            </Col>
            <Col span={5}>
              <Input
                size="small"
                placeholder="引用数"
                value={this.state.cited_times_limit}
                onChange={this.setSearchCitedTimes}
                onPressEnter={this.onSearchSubmit}
              />
            </Col>
          </InputGroup>
          <Button
            style={{ margin: "5px 0px" }}
            size="small"
            onClick={this.hideAdvance}
          >
            隐藏高级过滤
          </Button>
        </div>
      );
    } else {
      return (
        <div>
          <Select
            size="small"
            placeholder="选择文章学科"
            style={{ width: 130, margin: "5px 0px" }}
            onChange={this.handleDatabaseChange}
          >
            {databaseOpt.map(DB => (
              <Option key={DB}>{DB}</Option>
            ))}
          </Select>
          <Button
            style={{ margin: "0px 5px" }}
            size="small"
            onClick={this.showAdvance}
          >
            显示高级过滤
          </Button>
        </div>
      );
    }
  }

  render() {
    const expand = this.state.expand;
    const search_results = this.props.search_results;
    const addExample = this.props.addExample;
    const setSearchTerm = this.props.setSearchTerm;
    const setReferenceSearchTerm = this.props.setReferenceSearchTerm;
    const switchToRefSearch = this.props.switchToRefSearch;
    const onCitationSearchSubmit = this.props.onCitationSearchSubmit;
    const textClick = this.props.textClick;
    const resultFontSize = this.props.resultFontSize;
    const navigateSentence = this.navigateSentence;
    const viewFull = this.viewFull;

    return (
      <div key="example-search-bar" style={{ margin: "10px 0px" }}>
        <div style={{ margin: "5px 0px" }}>
          <font color="white">
            从数据库搜索您想书写的内容的例句。搜索时，为您搜索的搜索词搭配合用词汇可以提升搜索精确度（例如："ANOVA"
            => "ANOVA is applied"）。
          </font>
        </div>
        <Input
          value={this.props.search_term}
          onChange={setSearchTerm}
          onPressEnter={this.onSearchSubmit}
        />
        {this.renderAdvanceFilters()}
        <div style={{ margin: "5px 0px" }} />
        {// first, check whether system is loading data
        this.state.loading ? (
          <div>
            <font color="white">
              <b>正在从服务器读取内容...</b>
            </font>
          </div> // then, check for the empty result condition: length == 1 and cited_times < 0
        ) : search_results.length == 1 && search_results[0].cited_times < 0 ? (
          <div>
            <font color="white">
              <b>没有找到相关例句，请检查您的拼写和搜索内容</b>
            </font>
          </div>
        ) : (
          search_results.map((example, i) => {
            // define the onclick function for each list
            const onClicki = e => {
              var exp = expand;
              exp[i] = !exp[i];
              this.setState({ expand: exp });
            };

            const {
              title,
              journal,
              year,
              doc_id,
              sent_id,
              hit_text,
              hit_text_marked,
              cited_times,
              abbrev_text
            } = example;
            // text used as example sentence, not marked
            const joined_hit_text_template = hit_text.join(". ");
            // text for display, with current sentence marked
            const joined_hit_text_display = hit_text_marked.join(". ");

            function clickAdd(e) {
              // add the middle one (the actual text under search)
              addExample(hit_text[1]);
            }

            function clickPrevSent(e) {
              navigateSentence(i, -1);
            }

            function clickNextSent(e) {
              navigateSentence(i, 1);
            }

            function clickViewFull(e) {
              viewFull(i);
            }

            async function clickOneClickSearch(e) {
              setReferenceSearchTerm(title);
              // await for the result, or will show blank
              await switchToRefSearch(e);
              onCitationSearchSubmit();
              alert(
                "如果搜索没有找到文章，可尝试删除标题内非常规字符（包括'<>'等内容），之后按回车再次尝试"
              );
            }

            return (
              <div key={"example_" + i}>
                <div style={{ fontSize: resultFontSize }}>
                  <font color="white">
                    <b>{title}</b>
                  </font>
                </div>
                <div style={{ fontSize: resultFontSize }}>
                  <font color="white">
                    {journal +
                      " " +
                      year +
                      " 被 " +
                      cited_times +
                      " 篇论文引用"}
                  </font>
                </div>
                <ExpandableText
                  expandBool={expand[i]}
                  text={joined_hit_text_display}
                  abbrevText={abbrev_text}
                  onClick={onClicki}
                  textClick={textClick}
                  resultFontSize={resultFontSize}
                />
                <button
                  style={{ margin: "5px 0px", fontSize: resultFontSize }}
                  onClick={clickAdd}
                >
                  摘抄例句
                </button>
                <button
                  style={{ margin: "5px 0px", fontSize: resultFontSize }}
                  onClick={clickPrevSent}
                >
                  上一句
                </button>
                <button
                  style={{ margin: "5px 0px", fontSize: resultFontSize }}
                  onClick={clickNextSent}
                >
                  下一句
                </button>
                <button
                  style={{ margin: "5px 0px", fontSize: resultFontSize }}
                  onClick={clickViewFull}
                >
                  查看全文
                </button>
                <button
                  style={{ margin: "5px 0px", fontSize: resultFontSize }}
                  onClick={clickOneClickSearch}
                >
                  一键查找引用
                </button>
              </div>
            );
          })
        )}
      </div>
    );
  }
}

export default ExamplePanel;
