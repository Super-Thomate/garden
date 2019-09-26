#! /bin/bash

branch=`git branch | grep \* | awk '{ print $2 }'`
if [ "a$1" != "a" -a "a$1" != "amaster" -a "a$1" != "a$branch" ] ; then
  git push origin --delete $1;
  git fetch --all --prune
  git branch -D $1;
else
  echo "Cannot delete branch '$1'"
fi