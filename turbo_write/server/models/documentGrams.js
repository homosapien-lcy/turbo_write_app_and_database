const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const documentGramsSchema = new Schema({
  subject: {
    type: String,
    required: true
  },
  interpolation_model: {
    type: Map,
    // values must be numbers
    of: Number
  },
  unigram_freq: {
    type: Map,
    of: Number
  },
  bigram_freq: {
    type: Map,
    of: Number
  },
  trigram_freq: {
    type: Map,
    of: Number
  },
  bigram_dict: {
    type: Map,
    of: Array
  },
  trigram_dict: {
    type: Map,
    of: Array
  }
});

module.exports = documentGramsSchema;
