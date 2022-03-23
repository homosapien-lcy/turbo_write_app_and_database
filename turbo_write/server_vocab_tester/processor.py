import json
import requests

TOP_CUT_UNI = 8000
TOP_CUT_BI = 5000
TOP_CUT_TRI = 3000

interpolation_model = {
    'unigram': 1,
    'bigram': 5,
    'trigram': 15
}

req = requests.post('http://localhost:5000/api/saveDocGrams',
                    json={"subject": "test",
                          "interpolation_model": {'unigram': 1,
                                                  'bigram': 5,
                                                  'trigram': 15},
                          "unigram_freq": {"ha": 1000},
                          "bigram_freq": {"ha": 1000},
                          "trigram_freq": {"ha": 1000},
                          "bigram_dict": {"ha": ["ha", "test"]},
                          "trigram_dict": {"ha": ["ha", "test"]}})
