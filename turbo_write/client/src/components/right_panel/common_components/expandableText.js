import React, { Component } from "react";
import ReactHtmlParser, {
  processNodes,
  convertNodeToElement,
  htmlparser2
} from "react-html-parser";
import { doNothing } from "../../utils/systemUtils";

class ExpandableText extends React.Component {
  onTextClick = e => {
    // if onClick from props is not defined (ie, not passed in)
    // use do nothing
    if (this.props.textClick === undefined) {
      doNothing();
    } else {
      this.props.textClick(this.props.text);
    }
  };

  render() {
    var text_cursor_style;
    // if don't have text click, don't show the cursor
    if (this.props.textClick === undefined) {
      text_cursor_style = "text";
    } else {
      text_cursor_style = "pointer";
    }

    return (
      <div
        style={{
          fontFamily: "Times New Roman",
          fontSize: this.props.resultFontSize
        }}
        title={this.props.text}
      >
        {this.props.expandBool ? (
          <div style={{ margin: "5px 5px" }}>
            <div
              style={{ cursor: text_cursor_style }}
              onClick={this.onTextClick}
            >
              <font color="white">{ReactHtmlParser(this.props.text)}</font>
            </div>
            <button
              style={{ textAlign: "left", margin: "10px 5px" }}
              onClick={this.props.onClick}
            >
              收起
            </button>
          </div>
        ) : (
          <button style={{ textAlign: "left" }} onClick={this.props.onClick}>
            {ReactHtmlParser(this.props.abbrevText)} ... 点击展开全文
          </button>
        )}
      </div>
    );
  }
}

export default ExpandableText;
