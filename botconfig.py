import json
import os
import sys

# get the path to project root
dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
# print ("dir_path : "+dir_path)
# Instance name
instance = sys.argv[1]
# Config for this instance
with open(dir_path+'config.json') as json_file:  
  config = json.load(json_file)[instance]

# print (config)
