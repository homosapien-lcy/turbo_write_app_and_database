import { popText } from "./webpageUtils";

// combine all hints in a section and show
export function showAllSectionHints(hints) {
  var full_hint_text = "";

  hints.forEach((h, i) => {
    full_hint_text += "<div>" + (i + 1) + ". " + h + "</div>";
  });

  popText(full_hint_text);
}
