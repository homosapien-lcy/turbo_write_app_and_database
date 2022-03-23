import React, { Component } from "react";
import { Input, notification, Button } from "antd";
import Textbar from "./textbar";

import ImitationWriter from "./imitationEditor";

import { showAllSectionHints } from "../utils/sectionHintUtils";
import { segmentSentences } from "../utils/textProcessingUtils";

const { TextArea } = Input;

const messages = {
  complete: "本部分完工！下一步：",
  incomplete: "本部分还未完成，请您完成后再进入下一句。"
};

const giveHint = (message, hint) => {
  notification["info"]({
    message: message,
    description: hint
  });
};

class WritingZone extends React.Component {
  render() {
    const {
      text,
      part,
      currentRefImage,
      currentRefText,
      isShowHint,
      current_hints,
      setText,
      popImage,
      hints,
      hintAddOne,
      hintSubOne,
      suggestTemplate
    } = this.props;

    const current_hint_of_section = current_hints[part];
    const hintsForPart = hints[part];

    const hint = hintsForPart[current_hint_of_section];

    function next(e) {
      hintAddOne(part);

      // if not the end
      if (current_hint_of_section + 1 < hintsForPart.length) {
        // get the next one and display
        const hint_next = hintsForPart[current_hint_of_section + 1];
        giveHint(messages["complete"], hint_next);
      }

      /*
      // check whether the sentence is actually finished by counting the number of sentences
      if (segmentSentences(text[part]).length > current_hint_of_section) {
        hintAddOne(part);

        // if not the end
        if (current_hint_of_section + 1 < hintsForPart.length) {
          // get the next one and display
          const hint_next = hintsForPart[current_hint_of_section + 1];
          giveHint(messages["complete"], hint_next);
        }
      } else {
        giveHint(messages["incomplete"], "参见提示");
      }
      */
    }

    function previous(e) {
      hintSubOne(part);

      // if not the begin
      if (current_hint_of_section > 0) {
        // get the next one and display
        const hint_prev = hintsForPart[current_hint_of_section - 1];
        giveHint(messages["complete"], hint_prev);
      }

      /*
      // check whether the sentence is actually finished by counting the number of sentences
      if (segmentSentences(text[part]).length > current_hint_of_section) {
        hintSubOne(part);

        // if not the begin
        if (current_hint_of_section > 0) {
          // get the next one and display
          const hint_prev = hintsForPart[current_hint_of_section - 1];
          giveHint(messages["complete"], hint_prev);
        }
      } else {
        giveHint(messages["incomplete"], "参见提示");
      }
      */
    }

    // make setText function to handle text changing and saving
    function onChangeTextArea(e) {
      setText(part, e);
    }

    // make setText function to handle text changing and saving
    function onChangeImitationEditor(text_value, e) {
      setText(part, text_value);
    }

    function clickImage(e) {
      popImage(currentRefImage);
    }

    function viewAllHints(e) {
      showAllSectionHints(hintsForPart);
    }

    return (
      <div>
        <Textbar text={part} />
        <div style={{ visibility: isShowHint }}>
          {part == "Introduction" ? (
            <Textbar
              text={
                "您可以在右侧搜索栏的'从搜索引擎导入文献'使用关键词查找相关文章，例如'circular RNA function'"
              }
            />
          ) : (
            <span />
          )}
          <Textbar text={"写作提示：" + hint} />
          <div>
            {currentRefImage ? (
              <img
                src={currentRefImage}
                onClick={clickImage}
                style={{ margin: "5px 0px" }}
              />
            ) : (
              <span />
            )}
          </div>
          <div>{currentRefText ? <div>{currentRefText}</div> : <span />}</div>
          <Button title="上一个提示" icon="caret-left" onClick={previous} />
          <Button title="查看本小节大纲" onClick={viewAllHints}>
            查看本小节所有提示
          </Button>
          <Button title="下一个提示" icon="caret-right" onClick={next} />
          {/*// orginal method for text_area*/}
          {/*<TextArea
            autosize={true}
            style={{ margin: "5px 0px" }}
            value={text[part]}
            onChange={onChange}
          />*/}
          <div style={{ margin: "5px 0px" }}>
            <ImitationWriter
              Text={text[part]}
              Vocabularies={this.props.vocabularies}
              updateText={onChangeImitationEditor}
              setCursorLoc={this.props.setCursorLoc}
            />
          </div>
        </div>
      </div>
    );
  }
}

export default WritingZone;
