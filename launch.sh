#! /bin/bash
Instance=$1
if [ "a$Instance" != "a" ] ; then
  /usr/bin/python3 ./bot.py $Instance & echo "kill -9 $!" > ./stop_$Instance.sh
  /usr/bin/python3 ./auto_bot.py $Instance & echo "kill -9 $!" >> ./stop_$Instance.sh
  chmod +x ./stop_$Instance.sh
else
  echo "Missing parameters Instance"
fi
