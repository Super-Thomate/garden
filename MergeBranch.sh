#! /bin/bash
PatchToMerge=$1
Branch=$2

git pull;
git checkout $PatchToMerge;
git pull;
git checkout $Branch;
git pull;
git merge --squash $PatchToMerge 2>/tmp/Error_merge 1>/tmp/Log_merge ;
Res=$?
if [ a"$Res" != a0 ] ; then
  Error=`cat /tmp/Error_merge`
  echo "Git Merge ======>"
  echo "$Error"
  echo "<====== Git Merge"
  echo "Error during merge. Fix conflict then excute:"
  echo "git commit -am \"merge/$PatchToMerge\";"
  echo "git push;"
  echo "git push origin --delete $PatchToMerge;"
  echo "git fetch --all --prune ;"
  echo "git branch -D $PatchToMerge;"
else
  git commit -am "merge/$PatchToMerge";
  git push;
  git push origin --delete $PatchToMerge;
  git fetch --all --prune ;
  git branch -D $PatchToMerge;
fi
rm /tmp/Error_merge
rm /tmp/Log_merge
