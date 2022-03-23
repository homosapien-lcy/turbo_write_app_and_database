import React, { Component } from "react";

import { Input } from "antd";
import Textbar from "../writing_zone/textbar";

import { questions } from "../constants/guidelineConstants";

class GuidelineBox extends React.Component {
  render() {
    const answers = this.props.answers;
    const setAnswers = this.props.setAnswers;

    return (
      <div>
        <div style={{ margin: "5px 0px" }} />
        <Textbar text="这个部分用于帮助您整理全文的写作思路，特别是Abstract和Introduction部分。请简要回答以下问题（仅作为理清思路用，不影响后续使用）：" />
        <div style={{ margin: "15px 0px" }} />
        {questions.map((Q, i) => {
          const setAnswersi = e => {
            setAnswers(i, e.target.value);
          };

          return (
            <div key={"Q" + i}>
              <Textbar text={Q} />
              <Input value={answers[i]} onChange={setAnswersi} />
            </div>
          );
        })}
      </div>
    );
  }
}

export default GuidelineBox;
