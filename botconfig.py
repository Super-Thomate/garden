import json
import sys

instance = sys.argv[1]
with open('config.json') as json_file:  
  config = json.load(json_file)[instance]

print (config)
