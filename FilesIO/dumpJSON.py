__author__ = 'amin'

import json

# Dumping a JSON file
jsonObj = {}
jsonObj["field1"] = [1,2,2,3]
jsonObj["field2"] = "NameofField"

filename = "C:/Amin/Python/FilesIO/" + "sample.json"
with open(filename, 'w') as outjson:
    json.dump(jsonObj, outjson)

