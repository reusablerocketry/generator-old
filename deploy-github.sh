#!/bin/sh

cd output
echo "Commit message:" `date`
git commit -am "`date`"
git push
