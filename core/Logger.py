import os
import sys
from datetime import datetime

def logger (come_from: str, text: str, output: str = None):
  """
  Print log information
  """
  # output is default => print ([DATETIME] from : text)
  # output is file_path => file_handler = open (file_path, "a"); file_handler.write ([DATETIME] from : text\n);file_handler.close()
  #ideally file_path : file_desc_YYYY_MM_DD.log(.err)
  now                        = datetime.now()
  str_date_time              = now.strftime ("%m/%d/%Y %H:%M:%S")
  if output is None:
    print ("[{0}] {1}: {2}".format(str_date_time, come_from, text))
  return