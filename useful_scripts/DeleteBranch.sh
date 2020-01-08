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

branch=`git branch | grep \* | awk '{ print $2 }'`
if [ "a$1" != "a" -a "a$1" != "amaster" -a "a$1" != "a$branch" ] ; then
  git push origin --delete $1;
  git fetch --all --prune
  git branch -D $1;
elif [ "a$1" = "amaster" ] ; then
  echo -e "${VP_RED}Cannot delete branch master !${VP_NONE}"
elif [ "a$1" = "a$branch" ] ; then
  echo -e "${VP_RED}Cannot delete current branch ($branch). Use 'git checkout master' first.${VP_NONE}"
else
  echo -e "${VP_RED}Cannot delete empty branch${VP_NONE}"
fi