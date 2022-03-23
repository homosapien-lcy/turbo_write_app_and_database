import React, { Component } from "react";
import { Upload, Icon, Modal, Input } from "antd";
import TextBox from "./textBox";

import { SERVER_ADDRESS } from "../constants/networkConstants";

const { TextArea } = Input;

class Figure extends React.Component {
  state = {
    inputMode: this.props.inputMode,
    previewVisible: false,
    previewImage: "",
    id: this.props.id
  };

  // method for upload box
  handleCancel = () => this.setState({ previewVisible: false });

  handlePreview = file => {
    this.setState({
      previewImage: file.url || file.thumbUrl,
      previewVisible: true
    });
  };

  updateFigure = ({ fileList }) => {
    this.props.changeFigure(this.state.id, fileList);
  };

  setUserInputBox = node => {
    this.userInputBox = node;
  };

  // method for text box
  emitEmpty = () => {
    this.userInputBox.focus();
    this.setState({ description: "" });
  };

  // method for restarting edit
  reEdit = () => {
    this.setState({ inputMode: true });
  };

  onChangeUserName = e => {
    this.props.changeDescription(this.state.id, e.target.value);
  };

  // handlers for 2 modes of text
  toInputMode = () => {
    this.setState({ inputMode: true });
  };

  toShowMode = () => {
    this.setState({ inputMode: false });
  };

  onPressEnter = () => {
    // first set to show mode
    this.toShowMode();
    this.props.changeToShowMode(this.state.id);
  };

  render() {
    const { previewVisible, previewImage } = this.state;
    // the close button for erasing input
    const suffix = this.props.description ? (
      <Icon type="close-circle" onClick={this.emitEmpty} />
    ) : (
      <span />
    );

    // a dummy request for disabling antd Upload's action
    const dummyRequest = ({ file, onSuccess }) => {
      setTimeout(() => {
        onSuccess("ok");
      }, 0);
    };

    const uploadButton = (
      <div>
        <Icon type="plus" />
        <div className="ant-upload-text">Upload</div>
      </div>
    );
    return (
      // {fileList.length >= 1 ? null : uploadButton} allows only 1 image
      <div className="clearfix" style={{ margin: "20px 0px" }}>
        <Upload
          // overwrite the request
          customRequest={dummyRequest}
          action={`${SERVER_ADDRESS}/api/placeholder`}
          listType="picture-card"
          fileList={this.props.fileList}
          onPreview={this.handlePreview}
          onChange={this.updateFigure}
        >
          {this.props.fileList != undefined && this.props.fileList.length >= 1
            ? null
            : uploadButton}
        </Upload>
        <Modal
          visible={previewVisible}
          footer={null}
          onCancel={this.handleCancel}
        >
          <img alt="figure" style={{ width: "100%" }} src={previewImage} />
        </Modal>
        <TextBox
          description={this.props.description}
          emitEmpty={this.emitEmpty}
          inputMode={this.state.inputMode}
          onChangeUserName={this.onChangeUserName}
          setUserInputBox={this.setUserInputBox}
          onPressEnter={this.onPressEnter}
          reEdit={this.reEdit}
        />
      </div>
    );
  }
}

export default Figure;
