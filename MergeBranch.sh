#! /bin/bash
PatchToMerge=$1
Branch=$2

git pull;
git checkout $PatchToMerge;
git pull;
git checkout $Branch;
git pull;
git merge --squash $PatchToMerge;
git commit -am "merge/$PatchToMerge";
git push;
git push origin --delete $PatchToMerge;
git fetch --all --prune ;
git branch -D $PatchToMerge;