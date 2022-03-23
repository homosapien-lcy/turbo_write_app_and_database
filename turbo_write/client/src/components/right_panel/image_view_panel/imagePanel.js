import React, { Component } from "react";

import ExpandableText from "../common_components/expandableText";

class ImagePanel extends React.Component {
  constructor(props) {
    super(props);
    this.state = { expand: {} };

    // initialize expand
    for (var i = 0; i < this.props.listOfFigureContents.length; i++) {
      this.state.expand[i] = false;
    }
  }

  render() {
    const listOfFigureContents = this.props.listOfFigureContents;
    const props = this.props;
    const expand = this.state.expand;

    // this solves the "this" undefined problem
    const setStateFun = new_state => {
      this.setState(new_state);
    };

    return (
      <div key="image_panel">
        {Object.keys(listOfFigureContents).map(function(k, i) {
          // map the keys to the contents
          const content = listOfFigureContents[k];
          const panel_key = "panel_" + k;

          function imageClickK() {
            props.imageClick(k);
          }

          // define the onclick function for each list
          const onClicki = e => {
            var exp = expand;
            exp[i] = !exp[i];
            setStateFun({ expand: exp });
          };

          if (content.fileList != undefined && content.fileList[0]) {
            return (
              <div key={panel_key} style={{ margin: "20px 20px" }}>
                <img
                  src={content.fileList[0].thumbUrl}
                  onClick={imageClickK}
                  style={{ cursor: "pointer" }}
                  style={{ margin: "10px 0px" }}
                />
                <br />
                <ExpandableText
                  expandBool={expand[i]}
                  text={content.description}
                  abbrevText={content.description.slice(0, 250)}
                  onClick={onClicki}
                  resultFontSize={props.resultFontSize}
                />
              </div>
            );
          } else {
            return <span key={panel_key} />;
          }
        })}
      </div>
    );
  }
}

export default ImagePanel;
