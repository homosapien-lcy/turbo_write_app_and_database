import React, { Component } from "react";
import { Col, Row, Input, Button, Select } from "antd";

import ExpandableText from "../common_components/expandableText";

import { searchForEvidence } from "../../utils/evidenceUtils";

class EvidencePanel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // requirement for journal name
      journal_name_must: "",
      // limit journals to be after year_limit
      year_limit: "",
      cited_times_limit: "",
      expand: {},
      loading: false
    };

    // initialize expand
    for (var i = 0; i < this.props.search_results.length; i++) {
      this.state.expand[i] = false;
    }
  }

  onSearchSubmit = async () => {
    this.setState({ loading: true });
    const evidence_results = await searchForEvidence(this.props.search_term);
    this.props.setSearchResults(evidence_results);
    this.setState({ loading: false });
  };

  render() {
    const expand = this.state.expand;
    const search_results = this.props.search_results;
    const setSearchTerm = this.props.setSearchTerm;
    const setReferenceSearchTerm = this.props.setReferenceSearchTerm;
    const switchToRefSearch = this.props.switchToRefSearch;
    const onCitationSearchSubmit = this.props.onCitationSearchSubmit;
    const resultFontSize = this.props.resultFontSize;

    return (
      <div key="evidence-search-bar" style={{ margin: "10px 0px" }}>
        <div style={{ margin: "5px 0px" }}>
          <font color="white">
            从数据库搜索您想要查找的Introduction和Discussion引用论据。
          </font>
        </div>
        <Input
          value={this.props.search_term}
          onChange={setSearchTerm}
          onPressEnter={this.onSearchSubmit}
        />
        <div style={{ margin: "5px 0px" }} />
        {// first, check whether system is loading data
        this.state.loading ? (
          <div>
            <font color="white">
              <b>正在从服务器读取内容...</b>
            </font>
          </div> // then, check for the empty result condition: length == 1 and cited_times < 0
        ) : (
          search_results.map((evidence, i) => {
            const title = evidence.title;
            const abstract = evidence.abstract;

            // define the onclick function for each list
            const onClicki = e => {
              var exp = expand;
              exp[i] = !exp[i];
              this.setState({ expand: exp });
            };

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
              <div>
                <div style={{ fontSize: resultFontSize }}>
                  <font color="white">
                    <b>{title}</b>
                  </font>
                </div>
                <ExpandableText
                  expandBool={expand[i]}
                  text={abstract}
                  abbrevText={abstract.slice(0, 250)}
                  onClick={onClicki}
                  resultFontSize={resultFontSize}
                />
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

export default EvidencePanel;
