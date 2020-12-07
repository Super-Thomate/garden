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


git pull;
git checkout develop;
git pull;
git checkout master;
git pull;
git merge develop 2>/tmp/Error_merge 1>/tmp/Log_merge ;
Res=$?
if [ a"$Res" != a0 ] ; then
  Error=`cat /tmp/Error_merge`
  echo -e "${VP_RED}Git Merge ======>"
  echo -e "$Error"
  echo -e "<====== Git Merge${VP_NONE}"
  echo -e "${VP_RED}Error during merge. Fix conflict then excute:${VP_NONE}"
  echo -e "${VP_YELLOW}git commit -am \"merge/develop\";"
  echo -e "git push;"
  echo -e "git push origin --delete develop;"
  echo -e "git fetch --all --prune ;"
  echo -e "git branch -D develop;"
  echo -e "git checkout -b develop master;"
  echo -e "git push origin develop;"
  echo -e "git push --set-upstream origin develop;${VP_NONE}"
else
  git commit -am "merge/develop";
  git push;
  git push origin --delete develop;
  git fetch --all --prune ;
  git branch -D develop;
  git checkout -b develop master;
  git push origin develop;
  git push --set-upstream origin develop;
fi
rm /tmp/Error_merge
rm /tmp/Log_merge
