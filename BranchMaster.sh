#! /bin/bash

if [ "a$1" != "a" ] 
then
git checkout master;
git pull;
git checkout -b $1 master;
git push origin $1;
git push --set-upstream origin $1;
else
echo "Missing parameters branch name."
fi