import React, { Component } from "react";
import { questions } from "../../constants/guidelineConstants";

class GuidelinePanel extends React.Component {
  render() {
    const answers = this.props.answers;

    return (
      <div style={{ margin: "10px 0px" }}>
        {questions.map((q, i) => {
          return (
            <div key={"side_bar_qa_" + i} style={{ margin: "5px 0px" }}>
              <div>
                <font color="white">{q}</font>
              </div>
              <div>
                <font color="white">{answers[i]}</font>
              </div>
            </div>
          );
        })}
      </div>
    );
  }
}

export default GuidelinePanel;
