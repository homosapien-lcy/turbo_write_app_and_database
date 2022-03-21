const PDFJS = require("pdfjs-dist");
PDFJS.GlobalWorkerOptions.workerSrc = "pdfjs-dist/build/pdf.worker.js";
const fs = require("fs");

var in_name = process.argv[2];
var out_name = in_name.substr(0, in_name.length - 4) + ".txt";

function flattenArr(arr) {
  return [].concat.apply([], arr);
}

// join all text into 1
function combineText(texts) {
  return texts.items.map(x => x.str).join(" ");
}

// collect all promises from docs
function collectFilePromises(doc) {
  const filePromises = [];
  for (pn = 1; pn <= doc._pdfInfo.numPages; pn++) {
    filePromises.push(doc.getPage(pn));
  }

  return filePromises;
}

function saveAsTxt(text, outname) {
  fs.writeFile(outname, text, function(err) {
    if (err) {
      return console.log(err);
    }

    console.log(outname + " has been saved!");
  });
}

function collectTextAndSave(docname, outname) {
  var pdf_file = PDFJS.getDocument(docname);
  pdf_file.promise.then(function(pdfDocument) {
    pdf_promises = collectFilePromises(pdfDocument);
    Promise.all(pdf_promises)
      // extract content promises
      .then(pages => pages.map(x => x.getTextContent()))
      .then(texts =>
        // collect all texts and send as a string
        Promise.all(texts).then(textContents => {
          const allTextInEachDoc = textContents.map(x => combineText(x));
          const allText = allTextInEachDoc.join(" ");
          saveAsTxt(allText, outname);
        })
      );
  });
}

collectTextAndSave(in_name, out_name);
