import json
import os

lang_files_dir = os.path.dirname(
  os.path.realpath(__file__)) + '/../language_files/'  # Path to the language_files directory
master_file = lang_files_dir + 'fr.json'  # Path to the master file
slave_files = [lang_files_dir + filename for filename in ['en.json']]  # Path to the slave files

if __name__ == '__main__':
  with open(master_file, encoding='utf-8') as file:
    master_dict = json.load(file)

  for path in slave_files:
    with open(path, encoding='utf-8') as file:
      slave_dict = json.load(file)
      for key in master_dict.keys():
        if not key in slave_dict:
          print(f"Missing key `{key}` in file `{path.split('/')[-1]}`")
