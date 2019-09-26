#! /bin/bash

branch=`git branch | grep \* | awk '{ print $2 }'`
if [ "a$1" != "a" -a "a$1" != "amaster" -a "a$1" != "a$branch" ] ; then
  git push origin --delete $1;
  git fetch --all --prune
  git branch -D $1;
elif [ "a$1" = "amaster" ] ; then
  echo "Cannot delete branch master !"
elif [ "a$1" = "a$branch" ] ; then
  echo "Cannot delete current branch ($branch). Use 'git checkout master' first."
else
  echo "Cannot delete empty branch"
fi