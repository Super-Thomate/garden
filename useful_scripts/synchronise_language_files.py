import json
import os

master_file_name = 'fr.json'
slaves_files_name = ['en.json']

dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
if __name__ == '__main__':
    master_file = open(f'{dir_path}../language_files/{master_file_name}', 'r')
    slaves_files = []
    for name in slaves_files_name:
      slaves_files.append(open(f'{dir_path}../language_files/{name}', 'r'))

    master = json.load(master_file)
    slaves = []
    for slave in slaves_files:
      slaves.append(json.load(slave))


    for index, slave in enumerate(slaves, start=0):
      new_slave = {}
      for key in master.keys():
        try:
          new_slave[key] = slave[key]
        except KeyError as e:
          print(f'KeyError: {key} for file {slaves_files_name[index]}.')
          new_slave[key] = '**********************************************'
        except Exception as e:
          print(e)
      if len(new_slave) != 0:
        with open(f'{dir_path}../language_files/NEW_{slaves_files_name[index]}', 'w+') as new_file:
          json.dump(new_slave, new_file)

    master_file.close()
    for index, file in enumerate(slaves_files, start=0):
      file.close()

