import React, { Component } from "react";

import { UnControlled as CodeMirror } from "react-codemirror2";
// hint has to be imported from the js codemirror library
import CM from "codemirror/lib/codemirror";

import "codemirror/lib/codemirror.css";
// javascript mode contains the definition for token, if not imported
// the whole line will be recognized as a single token
import "./hint_methods/javascript";
import "codemirror/theme/monokai.css";
import "codemirror/theme/material.css";
import "codemirror/addon/hint/show-hint.css";

import "./hint_methods/showHint";
import "./hint_methods/myHint";

class ImitationEditor extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const options = {
      //theme: "monokai",
      theme: "default",
      lineWrapping: true
    };

    /* 
    give the classname for formating in css
    onKeyPress event works much better than onKeyUp, onKeyDown
    and onInput
    */
    const mirrorInstance = (
      <div>
        <CodeMirror
          className="ReactCodeMirror2"
          value={this.props.Text}
          options={options}
          style={{ height: "100%" }}
          onKeyPress={(editor, e) => {
            editor.showHint(CM.hint.mine, this.props.Vocabularies);
          }}
          onChange={(editor, e) => {
            const cursor = editor.getCursor();
            this.props.updateText(editor.getValue(), e);
            // set the cursor to the location before rerendering
            editor.setCursor({ line: cursor.line, ch: cursor.ch });
          }}
          onCursorActivity={editor => {
            const line_num = editor.getCursor().line;
            const pos_in_line = editor.getCursor().ch;
            // set the cursor to the location before rerendering
            this.props.setCursorLoc(line_num, pos_in_line);
          }}
          onSelection={(editor, data) => {
            const start = data.ranges[0].anchor;
            const end = data.ranges[0].head;
            console.log("selected area:", start, end);
          }}
        />
      </div>
    );

    return mirrorInstance;
  }
}

export default ImitationEditor;
