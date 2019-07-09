import json
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
print ("dir_path : "+dir_path)
instance = sys.argv[1]
with open(dir_path+'config.json') as json_file:  
  config = json.load(json_file)[instance]

print (config)
