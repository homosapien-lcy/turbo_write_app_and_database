const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const turboWriteSchema = new Schema({
  profileID: {
    type: String,
    unique: true
  },
  guideline_answers: {
    type: Array,
    of: String
  },
  title: {
    type: String
  },
  text: {
    type: Map,
    of: String
  },
  descriptions: {
    type: Map,
    of: String
  },
  figures: {
    type: Map,
    of: { data: Buffer, contentType: String }
  },
  references: {
    type: String
  },
  references_index: {
    type: String
  },
  references_lookup: {
    type: String
  },
  citation_counts: {
    type: String
  }
});

module.exports = turboWriteSchema;
