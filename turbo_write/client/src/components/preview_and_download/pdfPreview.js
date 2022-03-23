import React, { Component } from "react";
import { Button } from "antd";

import {
  Document as PdfDocument,
  Page as PdfPage,
  Text as PdfText,
  View as PdfView,
  StyleSheet as PdfStyleSheet,
  Font as PdfFont
} from "@react-pdf/renderer";
import PdfParagraphs from "./paragraphs";

import { saveDocx } from "../utils/docxUtils";
import { sortedCitationsGen, processCitations } from "../utils/citationUtils";

import Textbar from "../writing_zone/textbar";

// register font
PdfFont.register("./Fonts/Times_New_Roman.ttf", { family: "Times_New_Roman" });

// Create styles
const styles = PdfStyleSheet.create({
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
  text: {
    fontFamily: "Times_New_Roman"
  },
  title: {
    fontFamily: "Times_New_Roman",
    fontSize: 20
  }
});

class PDFPreview extends React.Component {
  constructor(props) {
    super(props);

    // unpack contents
    const { title, text, referencesLookup, listOfFigureContents } = this.props;

    const references = sortedCitationsGen(text, referencesLookup);
    const ref_processed_text = processCitations(
      text,
      references,
      referencesLookup
    );

    this.state = {
      title: title,
      text: ref_processed_text,
      references: references,
      listOfFigureContents: listOfFigureContents
    };
  }

  render() {
    const { title, text, references, listOfFigureContents } = this.state;

    const clickSaveDocx = e => {
      saveDocx(title, text, references, listOfFigureContents);
    };

    return (
      <div>
        <Textbar text="提示：下载后引用文献会显示为上标" />
        <Button style={{ margin: "5px 0px" }} onClick={clickSaveDocx}>
          下载全文
        </Button>
        <PdfDocument>
          <PdfPage size="A4" style={styles.page}>
            <div
              key={"main_title"}
              style={{ "font-weight": "bold", "text-align": "center" }}
            >
              <PdfView style={styles.row}>
                <PdfText style={styles.title}>{title}</PdfText>
                <PdfView style={styles.fill1} />
              </PdfView>
            </div>
            {Object.entries(text).map(([part_k, part_text]) => {
              return (
                <div key={part_k}>
                  <div
                    key={"title_" + part_k}
                    style={{ "font-weight": "bold" }}
                  >
                    <PdfView style={styles.row}>
                      <PdfText style={styles.text}>{part_k}</PdfText>
                      <PdfView style={styles.fill1} />
                    </PdfView>
                  </div>
                  <div key={"section_" + part_k}>
                    <PdfView style={styles.row}>
                      <PdfParagraphs text={part_text} />
                      <PdfView style={styles.fill1} />
                    </PdfView>
                  </div>
                </div>
              );
            })}
            <div key={"references"}>
              <div key={"title_references"} style={{ "font-weight": "bold" }}>
                <PdfView style={styles.row}>
                  <PdfText style={styles.text}>References</PdfText>
                  <PdfView style={styles.fill1} />
                </PdfView>
              </div>
              {references.map((citation_text, i) => {
                // citation index starts from 1
                const citation_index = i + 1;
                // extract and form citation
                const citation = citation_index + " " + citation_text;

                return (
                  <div key={"reference_" + citation_index}>
                    <PdfView style={styles.row}>
                      <PdfParagraphs text={citation} />
                      <PdfView style={styles.fill1} />
                    </PdfView>
                  </div>
                );
              })}
            </div>
          </PdfPage>
        </PdfDocument>
      </div>
    );
  }
}

export default PDFPreview;
