#! /bin/bash
# DATE=`date "+%Y-%m-%d %H:%M:%S"`
branch=`git branch | grep \* | awk '{ print $2 }'`
if [  "a$1" = "a"  ]
then
  message=$branch
else
  message=$1
fi

git commit -am "$message" ;
git push ;
