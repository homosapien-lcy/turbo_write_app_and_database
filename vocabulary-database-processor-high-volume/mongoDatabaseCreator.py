import requests

from python_utils.processorUtils import *

data_json_fn = sys.argv[1]

json_data = loadJsonData(data_json_fn)
print(json_data)

req = requests.post('http://localhost:5000/api/saveDocGrams',
                    json=json_data)

print(req)
