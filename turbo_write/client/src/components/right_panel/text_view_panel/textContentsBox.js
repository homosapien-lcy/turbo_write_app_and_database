import React, { Component } from "react";

import ExpandableText from "../common_components/expandableText";
import { textToParagraph } from "../../utils/textProcessingUtils";

class TextContentsBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = { expand: {} };

    // initialize expand
    const text_entries = Object.entries(this.props.text);
    for (var j = 0; j < text_entries.length; j++) {
      const [part_k, part_text] = text_entries[j];
      const text_seg = part_text.split("\n");
      // set 1 for each element, with a compound key of part and index
      for (var i = 0; i < text_seg.length; i++) {
        this.state.expand[part_k + "_" + i] = false;
      }
    }
  }

  render() {
    return (
      <div>
        {Object.entries(this.props.text).map(([part_k, part_text]) => {
          return (
            <div key={part_k}>
              <div
                style={{
                  fontFamily: "Times New Roman",
                  fontSize: this.props.resultFontSize,
                  margin: "10px 0px"
                }}
              >
                <font color="white">{part_k}</font>
              </div>
              {textToParagraph(part_text).map((paragraph, i) => {
                // function for clicking
                const onClickpartki = e => {
                  var expand = this.state.expand;
                  expand[part_k + "_" + i] = !expand[part_k + "_" + i];
                  this.setState({ expand: expand });
                };

                return (
                  <ExpandableText
                    expandBool={this.state.expand[part_k + "_" + i]}
                    text={paragraph}
                    abbrevText={paragraph.slice(0, 250)}
                    onClick={onClickpartki}
                    resultFontSize={this.props.resultFontSize}
                  />
                );
              })}
            </div>
          );
        })}
      </div>
    );
  }
}

export default TextContentsBox;
