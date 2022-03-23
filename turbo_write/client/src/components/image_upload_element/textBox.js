import React, { Component } from "react";
import { Icon, Input } from "antd";
const { TextArea } = Input;

class TextBox extends React.Component {
  render() {
    const description = this.props.description;

    // the close button for erasing input
    const removeInputButton = description ? (
      <Icon type="close-circle" onClick={this.props.emitEmpty} />
    ) : (
      <span />
    );

    const reEditButton = <Icon type="edit" onClick={this.props.reEdit} />;

    if (this.props.inputMode) {
      return (
        <div>
          <TextArea
            placeholder="请输入图片描述"
            value={description}
            onChange={this.props.onChangeUserName}
            // this.userInputBox just need to match the one in emitEmpty
            ref={this.props.setUserInputBox}
            onPressEnter={this.props.onPressEnter}
            autosize
          />
        </div>
      );
    } else {
      return (
        <div>
          <div>{description}</div>
          {reEditButton}
        </div>
      );
    }
  }
}

export default TextBox;
