import axios from "axios";

import { SERVER_ADDRESS } from "../constants/networkConstants";

export async function searchForEvidence(search_term) {
  const response = await axios.post(`${SERVER_ADDRESS}/api/evidence`, {
    query: search_term
  });

  const hits = response.data.hits;
  return hits;
}
