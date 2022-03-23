// a dropdown menu that hides when menu is click
import React, { Component } from "react";

import { Dropdown, Button, Menu } from "antd";
const { SubMenu } = Menu;

class OverlayDropdown extends React.Component {
  state = {
    visible: false
  };

  hideSubMenu = e => {
    this.setState({ visible: false });
  };

  handleVisibleChange = flag => {
    this.setState({ visible: flag });
  };

  render() {
    const menu = (
      <Menu>
        {this.props.submenu_components.map(([title, onClickFun]) => {
          const onSubMenuClick = e => {
            // run the click function
            onClickFun(e);
            // hide submenu
            this.hideSubMenu(e);
          };

          return (
            <SubMenu key={title} title={title} onTitleClick={onSubMenuClick} />
          );
        })}
      </Menu>
    );

    return (
      <Dropdown
        overlay={menu}
        onVisibleChange={this.handleVisibleChange}
        visible={this.state.visible}
      >
        <Button
          style={{ margin: "0px 20px" }}
          shape="circle"
          icon={this.props.icon_name}
        />
      </Dropdown>
    );
  }
}

export default OverlayDropdown;
