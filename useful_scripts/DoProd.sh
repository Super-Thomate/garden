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

Patch=$1

git pull;
git checkout $Patch;
git pull;
git checkout develop;
git pull;
git merge $Patch 2>/tmp/Error_merge 1>/tmp/Log_merge ;
Res=$?
if [ a"$Res" != a0 ] ; then
  Error=`cat /tmp/Error_merge`
  echo -e "${VP_RED}Git Merge ======>"
  echo -e "$Error"
  echo -e "<====== Git Merge${VP_NONE}"
  echo -e "${VP_RED}Error during merge. Fix conflict then excute:${VP_NONE}"
  echo -e "${VP_YELLOW}git commit -am \"merge/$Patch\";"
  echo -e "git push;"
  echo -e "git push origin --delete $Patch;"
  echo -e "git fetch --all --prune ;"
  echo -e "git branch -D $Patch;${VP_NONE}"
else
  git commit -am "merge/$Patch";
  git push;
  git push origin --delete $Patch;
  git fetch --all --prune ;
  git branch -D $Patch;
fi
rm /tmp/Error_merge
rm /tmp/Log_merge
