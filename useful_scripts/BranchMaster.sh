#! /bin/bash

#styles
VP_NONE='\033[00m'
VP_RED='\033[01;31m'
VP_GREEN='\033[01;32m'
VP_YELLOW='\033[01;33m'
VP_PURPLE='\033[01;35m'
VP_CYAN='\033[01;36m'
VP_WHITE='\033[01;37m'
VP_BOLD='\033[1m'
VP_UNDERLINE='\033[4m'

if [ "a$1" != "a" ] ; then
  git checkout master  2>/tmp/Error_$$ 1>/tmp/Log_$$ ;
  Res=$?
  if [ a"$Res" != a0 ] ; then
    Error=`cat /tmp/Error_$$`
    echo -e "${VP_RED}Git Checkout Master ======>"
    echo "$Error"
    echo -e "<====== Git Checkout Master${VP_NONE}"
  else
    git pull;
    git checkout -b $1 master;
    git push origin $1;
    git push --set-upstream origin $1;
  fi
  else
  echo -e "${VP_RED}Missing parameters branch name.${VP_NONE}"
fi