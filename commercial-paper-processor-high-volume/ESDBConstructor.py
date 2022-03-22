import sys
import time
import json
import urllib3
import uuid
import copy

from elasticsearch import Elasticsearch
'''
helpers.bulk is much better than es.bulk, which needs
specific formatting
'''
from elasticsearch import helpers

per_batch = 100000

# collect all filenames to upload
json_filename_list = sys.argv[1:]

collection_name = json_filename_list[0].split('_')[0].strip()
print('uploading to collection:', collection_name)

# mapping with analyzer
# in professional searches, the analyzer actually make search inaccurate
# but can increase the possible selections, thus chosen
paper_collection_settings = {
    'settings': {
        'analysis': {
            "analyzer": {
                "paper_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "trim",
                        "snowball_stemmer",
                        "english_stop"
                    ]
                }
            },
            "filter": {
                "snowball_stemmer": {
                    "type": "snowball",
                    "language": "english"
                },
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                }
            }
        }
    },
    'mappings': {
        'properties': {
            'content': {
                'type': 'text',
                'analyzer': 'paper_analyzer',
                'search_analyzer': 'paper_analyzer',
                'norms': 'false'
            },
            'cited_times': {
                "type": "integer"
            }
        }
    }
}

'''
# mapping without analyzer
paper_collection_settings = {
    'settings': {
        'analysis': {
            "analyzer": {
                "paper_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "trim",
                        "snowball_stemmer",
                        "english_stop"
                    ]
                }
            },
            "filter": {
                "snowball_stemmer": {
                    "type": "snowball",
                    "language": "english"
                },
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                }
            }
        }
    },
    'mappings': {
        'properties': {
            'cited_times': {
                "type": "integer"
            }
        }
    }
}
'''

# port is set to 9200 by default
_es = Elasticsearch("http://localhost:9200")

# if exist, delete first
if _es.indices.exists(index=collection_name) is True:
    _es.indices.delete(index=collection_name)

_es.indices.create(index=collection_name, body=paper_collection_settings)


# insert with timeout exception handling
def bulkInsertData(es_db, cur_upload_data):
    try:
        response = helpers.bulk(es_db, cur_upload_data)
        return response
    # when run into error
    except Exception as e:
        print('run into error:', e)
        print('try again in 3 minutes')
        # wait
        time.sleep(180)
        # try again
        return bulkInsertData(es_db, cur_upload_data)


# upsert can avoid duplication
def addUpsertOps(upload_data):
    upload_data_upsert = []
    for d in upload_data:
        # copy
        d_copy = copy.deepcopy(d)
        # remove '_index' to prevent meta field error
        d_copy.pop('_index', None)
        d_copy['index'] = d['_index']

        d_upsert = {
            '_op_type': 'update',
            '_index': d['_index'],
            # use uuid to create an unique id
            '_id': str(uuid.uuid5(uuid.NAMESPACE_DNS, d['content'])),
            'doc': d_copy,
            # use upsert to remove duplicates
            'doc_as_upsert': True
        }
        upload_data_upsert.append(d_upsert)

    return upload_data_upsert


# collect data
data_box = []
for json_filename in json_filename_list:
    print("uploading:", json_filename)
    json_file = open(json_filename, 'r')
    # read line by line to save memory
    for line_num, line in enumerate(json_file):
        print("uploading part", line_num)
        # convert string to json with loads
        upload_data = json.loads(line)

        data_box.extend(upload_data)

    json_file.close()

print("total amount of data:", len(data_box))

# upload to db
for i in range(0, len(data_box), per_batch):
    # get batch
    cur_data_box = data_box[i: i+per_batch]
    # add upsert op
    cur_data_box = addUpsertOps(cur_data_box)
    response = bulkInsertData(_es, cur_data_box)
    print("response:", response)
