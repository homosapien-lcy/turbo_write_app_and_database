import {
  Document as docDocument,
  Paragraph as docParagraph,
  TextRun as docTextRun,
  Packer as docPacker
} from "docx";
import FileSaver from "file-saver";

import { splitByCitation, isCitation } from "./citationUtils";
import { getImageSize } from "./fileProcessingUtils";
import { max_image_width } from "../constants/wordFormattingConstans";

export function saveDocx(title, text, references, listOfFigureContents) {
  const doc = new docDocument();
  // styles
  /* ------------------------------------------ */
  doc.Styles.createParagraphStyle("mainTitle", "Main Title")
    .basedOn("Normal")
    .font("Times New Roman")
    .size(36)
    .bold()
    .center();

  doc.Styles.createParagraphStyle("sectionTitle", "Section Title")
    .basedOn("Normal")
    .font("Times New Roman")
    .size(24)
    .bold();

  doc.Styles.createParagraphStyle("mainText", "Main Text")
    .basedOn("Normal")
    .font("Times New Roman")
    .size(24);

  doc.Styles.createParagraphStyle("figureDescription", "Main Text")
    .basedOn("Normal")
    .font("Times New Roman")
    .size(17);
  /* ------------------------------------------ */

  // add main title
  doc.createParagraph(title).style("mainTitle");

  // add sections
  Object.entries(text).forEach(([part_k, part_text]) => {
    // first add title
    doc.createParagraph(part_k).style("sectionTitle");

    // compile citation regex
    const citation_regex = new RegExp(/(\[[0-9]+\])/g);

    // split by citation
    var part_text_sep_by_ref = splitByCitation(part_text);

    // filter out empty string, which will cause line
    // change in text run
    part_text_sep_by_ref = part_text_sep_by_ref.filter(t => {
      return t.length > 0;
    });

    // generate new paragraph
    var para = new docParagraph();
    part_text_sep_by_ref.forEach(t => {
      // convert t to text run
      var text_run = new docTextRun(t);
      // if the part is in citation form
      // add as superscript
      if (isCitation(t)) {
        para.addRun(text_run.superScript());
      } else {
        // else, add as it is
        para.addRun(text_run);
      }
    });

    // style the text
    doc.addParagraph(para.style("mainText"));
  });

  // reference title
  doc.createParagraph("References").style("sectionTitle");

  // reference main
  references.forEach((citation_text, i) => {
    // citation index starts from 1
    const citation_index = Number(i) + 1;
    // extract and form citation
    const citation = citation_index + " " + citation_text;
    doc.createParagraph(citation).style("mainText");
  });

  doc.createParagraph("").pageBreak();

  Object.keys(listOfFigureContents).forEach(async figure_id => {
    const cur_figure = listOfFigureContents[figure_id];
    const figure_file = cur_figure.fileList[0];
    const figure_description = cur_figure.description;

    const { width, height } = getImageSize(figure_file.thumbUrl);

    // resize if image too large
    var scaling_factor = 1;
    if (width > max_image_width) {
      scaling_factor = max_image_width / width;
    }
    const width_in_word = width * scaling_factor;
    const height_in_word = height * scaling_factor;

    // add figure
    doc.createImage(figure_file.originFileObj, width_in_word, height_in_word);
    // add description
    doc.createParagraph(figure_description).style("figureDescription");
  });

  const packer = new docPacker();
  packer.toBlob(doc).then(buffer => {
    // use FileSaver in place of fs works,
    // just make doc into blob instead of buffer
    FileSaver.saveAs(buffer, title + ".docx");
  });
}
