import json
import sys
import os

dir_path = os.getcwd()+'/'
print (dir_path)

instance = sys.argv[1]
with open(dir_path+'config.json') as json_file:  
  config = json.load(json_file)[instance]

print (config)
