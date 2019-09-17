#! /bin/bash
Instance=$1
if [ "a$Instance" != "a" ] ; then
  /usr/bin/python3 ./bot.py $Instance & echo $! > ./pid_$Instance.log
  /usr/bin/python3 ./auto_bot.py $Instance & echo $! >> ./pid_$Instance.log
else
  echo "Missing parameters Instance"
fi
