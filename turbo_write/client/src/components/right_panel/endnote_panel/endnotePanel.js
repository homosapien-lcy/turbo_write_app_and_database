import React, { Component } from "react";

import { endNoteToCitations } from "../../utils/textProcessingUtils";

import { Button, Input } from "antd";
const { TextArea } = Input;

class EndNotePanel extends React.Component {
  state = {
    endnote_content: ""
  };

  setText = e => {
    this.setState({ endnote_content: e.target.value });
  };

  clickAdd = e => {
    const paper_info = endNoteToCitations(this.state.endnote_content);
    this.props.setSearchResults(paper_info);
  };

  render() {
    return (
      <div className="endnote-tool" style={{ margin: "10px 0px" }}>
        <div style={{ margin: "5px 0px" }}>
          <font color="white">
            导入EndNote信息：请将EndNote的txt内容粘帖到以下输入框，之后选择您想添加的引用
          </font>
        </div>
        <TextArea value={this.state.endnote_content} onChange={this.setText} />
        <Button
          style={{ textAlign: "left", margin: "10px 0px" }}
          size="small"
          onClick={this.clickAdd}
        >
          导入
        </Button>
      </div>
    );
  }
}

export default EndNotePanel;
