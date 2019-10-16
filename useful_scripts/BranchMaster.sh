#! /bin/bash

if [ "a$1" != "a" ] ; then
  git checkout master  2>/tmp/Error_$$ 1>/tmp/Log_$$ ;
  Res=$?
  if [ a"$Res" != a0 ] ; then
    Error=`cat /tmp/Error_$$`
    echo "Git Checkout Master ======>"
    echo "$Error"
    echo "<====== Git Checkout Master"
  else
    git pull;
    git checkout -b $1 master;
    git push origin $1;
    git push --set-upstream origin $1;
  fi
  else
  echo "Missing parameters branch name."
fi