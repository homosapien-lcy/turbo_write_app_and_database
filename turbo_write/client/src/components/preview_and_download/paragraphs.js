import React, { Component } from "react";
import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  Font
} from "@react-pdf/renderer";

// Create styles
const styles = StyleSheet.create({
  page: {
    flexDirection: "row",
    backgroundColor: "#E4E4E4"
  },
  row: {
    flexGrow: 1,
    flexDirection: "row"
  },
  fill1: {
    width: "40%",
    backgroundColor: "#e14427"
  },
  header: {
    fontFamily: "Times_New_Roman_Bold"
  },
  text: {
    fontFamily: "Times_New_Roman"
  }
});

class Paragraphs extends React.Component {
  render() {
    var text_segments = this.props.text.split("\n");
    text_segments = text_segments.filter(seg => seg.length > 0);
    return text_segments.map((seg, i) => {
      return (
        <div key={"paragraph_" + i}>
          <View style={styles.row}>
            <Text style={styles.text}>{seg}</Text>
            <View style={styles.fill1} />
          </View>
        </div>
      );
    });
  }
}

export default Paragraphs;
