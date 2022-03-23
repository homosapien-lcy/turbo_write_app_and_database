import React, { Component } from "react";

import ExpandableText from "../common_components/expandableText";
import {
  generateCitation,
  generateShortCitation
} from "../../utils/textProcessingUtils";

class SearchResultBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = { expand: {} };

    // initialize expand
    for (var i = 0; i < this.props.search_result_list.length; i++) {
      this.state.expand[i] = false;
    }
  }

  render() {
    const { search_result_list, addReference, resultFontSize } = this.props;

    return search_result_list.map((info, i) => {
      const { title, abstract, link, journal, author } = info;

      // define the onclick function for each list
      const onClicki = e => {
        var expand = this.state.expand;
        expand[i] = !expand[i];
        this.setState({ expand: expand });
      };

      function onClick(e) {
        window.open(link, "popup", "width=800,height=800");
      }

      function cite(e) {
        // also remove blanks and extra spaces
        const citation_text = generateCitation(
          author.authors,
          title,
          journal.journal
        );

        const short_citation_text = generateShortCitation(
          author.authorsTextShort,
          journal.journalInfo.year,
          title
        );

        const citation_info = {
          citation: citation_text,
          citation_short: short_citation_text,
          title: title,
          author: author,
          journal: journal,
          link: link
        };

        addReference(citation_info);
      }

      // only display part of the abstract
      // the full abstract is in title which display fully when hover
      return (
        <div key={"info_" + i} style={{ margin: "5px 0px" }}>
          <div
            style={{ fontFamily: "Times New Roman", fontSize: resultFontSize }}
          >
            <font color="white">{"Search Result " + (i + 1)}</font>
          </div>
          <div
            style={{ fontFamily: "Times New Roman", fontSize: resultFontSize }}
          >
            <a href={link} onClick={onClick} target="popup">
              {title.trim().length == 0 ? "No Title" : title}
            </a>
            <button
              style={{ textAlign: "left", margin: "5px 5px" }}
              onClick={cite}
            >
              引用此文
            </button>
          </div>
          <ExpandableText
            expandBool={this.state.expand[i]}
            text={abstract}
            abbrevText={abstract.slice(0, 250)}
            onClick={onClicki}
            resultFontSize={resultFontSize}
          />
        </div>
      );
    });
  }
}

export default SearchResultBox;
