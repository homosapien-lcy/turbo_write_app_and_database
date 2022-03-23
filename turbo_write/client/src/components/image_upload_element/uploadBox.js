import React, { Component } from "react";
import { Icon, Input, Button } from "antd";
import Figure from "./figureUpload";

class UploadBox extends React.Component {
  render() {
    return (
      <div>
        {Object.entries(this.props.listOfFigureContents).map(([k, content]) => {
          // map the keys to the contents
          return (
            <div key={k}>
              <Figure
                id={k}
                inputMode={content.inputMode}
                description={content.description}
                fileList={content.fileList}
                changeFigure={this.props.changeFigure}
                changeDescription={this.props.changeDescription}
                changeToShowMode={this.props.changeToShowMode}
              />
            </div>
          );
        })}
        <Icon
          type="plus-square"
          onClick={this.props.addFigure}
          style={{ fontSize: 24 }}
        />
      </div>
    );
  }
}

export default UploadBox;
