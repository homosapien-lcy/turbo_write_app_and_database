const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const formidable = require("formidable");
const { XMLHttpRequest } = require("xhr2");

const elasticsearch = require("@elastic/elasticsearch");

const fs = require("fs");
const mongoose = require("mongoose");
// enable and disable some functions in the back to prevent deprecation
mongoose.set("useNewUrlParser", true);
mongoose.set("useCreateIndex", true);
mongoose.set("useFindAndModify", false);

const mongodbConnect = "mongodb://localhost/turboWrite";
mongoose.connect(mongodbConnect, { useNewUrlParser: true });

// schema of user save inputs
const turboWriteSchema = require("./models/turboWrite");
const turboWrite = mongoose.model("turboWriteDB", turboWriteSchema);

// schema of vocabulary gram schema
const documentGramsSchema = require("./models/documentGrams");
const documentGrams = mongoose.model("documentGramsDB", documentGramsSchema);

const elasticsearchConnect = "http://localhost:9200";
const elasticsearchClient = new elasticsearch.Client({
  node: elasticsearchConnect,
  log: "trace"
});

const pythonSubServerConnect = "http://localhost:4000/nexus";

const app = express();
app.use(cors());
// increase the size limit of request entity to 10MB
// for Error: request entity too large
app.use(bodyParser.json({ limit: "10mb", extended: true }));

app.post("/api/save", (req, res) => {
  const form = new formidable.IncomingForm();
  form.parse(req, function(err, fields, files) {
    // use parse to convert string to obj
    const profileID = JSON.parse(fields.profileID);
    const guideline_answers = JSON.parse(fields.guideline_answers);
    const title = JSON.parse(fields.title);
    const text = JSON.parse(fields.text);
    const descriptions = JSON.parse(fields.descriptions);
    const figures = {};
    // these three dictionaries have very complicated structures
    // thus save as strings with out parsing
    const references = fields.references;
    const references_index = fields.references_index;
    const references_lookup = fields.references_lookup;
    const citation_counts = fields.citation_counts;

    for (var key in files) {
      const fig = files[key];

      const contentType = fig.type;
      // read data from filepath on server
      const filepath = fig.path;
      const data = fs.readFileSync(filepath);

      figures[key] = {
        data: data,
        contentType: contentType
      };
    }

    const profile = {
      profileID: profileID,
      guideline_answers: guideline_answers,
      title: title,
      text: text,
      descriptions: descriptions,
      figures: figures,
      references: references,
      references_index: references_index,
      references_lookup: references_lookup,
      citation_counts: citation_counts
    };

    turboWrite.find({ profileID: profileID }).then(search_result => {
      // if already in database, update
      if (search_result.length > 0) {
        turboWrite
          // for findOneAndUpdate, a dictionary other than an instance should be passed
          // or will result in _id modification error
          .findOneAndUpdate({ profileID: profileID }, profile)
          .then(() => {
            turboWrite.find({ profileID: profileID }).then(returnData => {
              console.log(returnData);
              res.send("Update Success!");
            });
          });
      }
      // else save new
      else {
        turboWrite.create(profile).then(returnData => {
          console.log(returnData);
          res.send("Save Success!");
        });
      }
    });
  });
});

app.get("/api/load", (req, res) => {
  const profileID = req.query.profileID;
  const savedSession = turboWrite.find({ profileID: profileID });
  savedSession.then(profile => {
    res.send(profile);
  });
});

app.post("/api/saveDocGrams", (req, res) => {
  const vocab = req.body;
  const subject = vocab.subject;
  console.log(vocab);

  documentGrams.find({ subject: subject }).then(search_result => {
    // if already in database, update
    if (search_result.length > 0) {
      documentGrams
        // for findOneAndUpdate, a dictionary other than an instance should be passed
        // or will result in _id modification error
        .findOneAndUpdate({ subject: subject }, vocab)
        .then(() => {
          documentGrams.find({ subject: subject }).then(returnData => {
            console.log(returnData);
            res.send("Update Success!");
          });
        });
    }
    // else save new
    else {
      documentGrams.create(vocab).then(returnData => {
        console.log(returnData);
        res.send("Save Success!");
      });
    }
  });
});

app.get("/api/loadDocGrams", (req, res) => {
  const subject = req.query.subject;
  const vocabulary = documentGrams.find({ subject: subject });
  vocabulary.then(vocab => {
    res.send(vocab[0]);
  });
});

// a place holder location for antd upload
app.post("/api/placeholder", (req, res) => {
  res.send("Placeholder test sucess");
});

app.post("/api/search", (req, res) => {
  const search_req = req.body;
  const es_call = elasticsearchClient.search(search_req);
  es_call.then(result => {
    res.send(result);
  });
});

app.post("/api/evidence", (req, res) => {
  const search_req = req.body.query;
  const json = JSON.stringify({
    query: search_req
  });

  var xmlHttp = new XMLHttpRequest();
  // true for asynchronous
  xmlHttp.open("POST", pythonSubServerConnect, true);
  xmlHttp.onreadystatechange = () => {
    // wait for the response
    if (xmlHttp.readyState == XMLHttpRequest.DONE) {
      // convert response to objects
      const response_content = JSON.parse(xmlHttp.response);
      res.send(response_content);
    }
  };
  xmlHttp.setRequestHeader("Content-type", "application/json; charset=utf-8");
  xmlHttp.send(json);
});

app.listen(5000);

// start python subserver
const { PythonShell } = require("python-shell");

var processor = new PythonShell("evidenceSearchPreloaded.py", {
  mode: "text",
  pythonPath: "python3",
  scriptPath: "pythonSubServer/",
  args: [
    "/root/turbo_write/pubmed_title_abstract_sentence_embedding/",
    "flat",
    "pubmed_title_abstract",
    "/root/turbo_write/pubmed_title_abstract_idf_data_whole.pkl",
    "coverage",
    "/root/turbo_write/fastText-0.9.2/"
  ]
});
processor.on("message", message => {
  console.log(message);
});
