import React, { Component } from "react";

class Textbar extends React.Component {
  render() {
    return (
      <div style={{ fontSize: 15, margin: "5px 0px" }}>{this.props.text}</div>
    );
  }
}

export default Textbar;
