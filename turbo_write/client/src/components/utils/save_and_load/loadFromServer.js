import axios from "axios";
import { makeOnlineFile } from "../fileProcessingUtils";
import { SERVER_ADDRESS } from "../../constants/networkConstants";

export default function loadFromServer(profileID, updateFunc, callback) {
  axios
    .get(`${SERVER_ADDRESS}/api/load`, {
      params: {
        profileID: profileID
      }
    })
    .then(res => {
      // when there was saved data
      if (res.data.length > 0) {
        // unpack
        const {
          profileID,
          guideline_answers,
          title,
          text,
          descriptions,
          figures,
          references: references,
          references_index: references_index,
          references_lookup: references_lookup,
          citation_counts: citation_counts
        } = res.data[0];

        const listOfFigureContents = {};

        // construct figure list
        for (var key in figures) {
          const description = descriptions[key];
          const fig = figures[key];
          const online_image_file = makeOnlineFile(fig, key);

          listOfFigureContents[key] = {
            inputMode: false,
            description: description,
            fileList: [online_image_file]
          };
        }

        // update everything
        updateFunc(
          guideline_answers,
          title,
          text,
          listOfFigureContents,
          // convert the strings of map saved in db back to map
          JSON.parse(references),
          JSON.parse(references_index),
          JSON.parse(references_lookup),
          JSON.parse(citation_counts)
        );

        // indicate this is a saved session
        return true;
      }

      // indicated this is a new session
      return false;
    })
    .then(saved => {
      if (saved) {
        callback();
      }
    });
}
