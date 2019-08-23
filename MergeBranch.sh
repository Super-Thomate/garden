#! /bin/bash
PatchToMerge=$1
Branch=$2

git pull;
git checkout $PatchToMerge;
git pull;
git checkout $Branch;
git pull;
git merge --squash $PatchToMerge 2>/tmp/Error_$$ 1>/tmp/Log_$$ ;
Res=$?
if [ a"$Res" != a0 ] ; then
  Error=`cat /tmp/Error_$$`
  echo "Git Merge ======>"
  echo "$Error"
  echo "<====== Git Merge"
else
  git commit -am "merge/$PatchToMerge";
  git push;
  git push origin --delete $PatchToMerge;
  git fetch --all --prune ;
  git branch -D $PatchToMerge;
fi
rm /tmp/Error_$$
rm /tmp/Log_$$
