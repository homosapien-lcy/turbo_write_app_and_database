import React, { Component } from "react";

import {
  bibTexToCitation,
  enwToCitation,
  risToCitation
} from "../../utils/textProcessingUtils";

import { Button, Input } from "antd";
const { TextArea } = Input;

class AddFromText extends React.Component {
  state = {
    text_input: ""
  };

  setText = e => {
    this.setState({ text_input: e.target.value });
  };

  addCitation = (citationConvertMethod, e) => {
    // only add ref in certain parts
    if (
      this.props.part != "图片" &&
      this.props.part != "回顾并下载全文" &&
      this.props.part != "Guideline"
    ) {
      // check for empty input
      if (this.state.text_input.trim().length > 0) {
        const citation_info = citationConvertMethod(this.state.text_input);
        this.props.addReference(citation_info);
      } else {
        alert("请您粘帖引用文件内容后再尝试");
      }
    } else {
      alert(
        "请在正文部分（Abstract, Introduction, Methods, Results, Discussion, Acknowledgement）插入引用"
      );
    }
  };

  clickAddBibTex = e => {
    this.addCitation(bibTexToCitation, e);
  };

  clickAddEnw = e => {
    this.addCitation(enwToCitation, e);
  };

  clickAddRis = e => {
    this.addCitation(risToCitation, e);
  };

  render() {
    return (
      <div className="text-input-tool">
        <div>
          <font color="white">
            请用txt文档编辑器打开您的文件（或复制网页上内容）粘贴到下方输入框，并点击相应的文件格式选项
          </font>
        </div>
        <TextArea value={this.state.text_input} onChange={this.setText} />
        <Button
          style={{ textAlign: "left", margin: "10px 5px" }}
          size="small"
          onClick={this.clickAddBibTex}
        >
          从bibTex添加
        </Button>
        <Button
          style={{ textAlign: "left", margin: "10px 5px" }}
          size="small"
          onClick={this.clickAddEnw}
        >
          从enw添加
        </Button>
        <Button
          style={{ textAlign: "left", margin: "10px 5px" }}
          size="small"
          onClick={this.clickAddRis}
        >
          从ris添加
        </Button>
      </div>
    );
  }
}

export default AddFromText;
