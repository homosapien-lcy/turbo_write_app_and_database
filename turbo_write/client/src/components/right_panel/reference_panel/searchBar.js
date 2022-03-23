import React, { Component } from "react";
import { Input, Button } from "antd";

class SearchBar extends React.Component {
  render() {
    return (
      <div key="reference-search-bar">
        <div>
          <font color="white">从数据库搜索添加</font>
        </div>
        <Input
          value={this.props.search_term}
          onChange={this.props.setSearchTerm}
          onPressEnter={this.props.onCitationSearchSubmit}
        />
      </div>
    );
  }
}

export default SearchBar;
