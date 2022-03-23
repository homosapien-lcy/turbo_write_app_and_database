import request from "superagent";
import { SERVER_ADDRESS } from "../../constants/networkConstants";

export default function saveToServer(
  paper_id,
  guideline_answers,
  title,
  text,
  listOfFigureContents,
  references,
  references_index,
  references_lookup,
  citation_counts,
  callback
) {
  const req = request.post(`${SERVER_ADDRESS}/api/save`);

  const descriptions = {};
  for (var key in listOfFigureContents) {
    const figure_content = listOfFigureContents[key];
    const description = figure_content.description;
    const figure_file = figure_content.fileList[0];

    // make sure the file has been uploaded
    if (figure_file) {
      // process descriptions
      descriptions[key] = description;

      // attach figure files to requests
      req.attach(key, figure_file.originFileObj);
    }
  }

  // for superagent, the client side needs to JSON.stringify
  req.field("profileID", JSON.stringify(paper_id));
  req.field("guideline_answers", JSON.stringify(guideline_answers));
  req.field("title", JSON.stringify(title));
  req.field("text", JSON.stringify(text));
  req.field("descriptions", JSON.stringify(descriptions));
  req.field("references", JSON.stringify(references));
  req.field("references_index", JSON.stringify(references_index));
  req.field("references_lookup", JSON.stringify(references_lookup));
  req.field("citation_counts", JSON.stringify(citation_counts));
  req.then(callback);
}
