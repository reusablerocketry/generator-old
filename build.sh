#!/bin/sh

rm output/* -rf
mkdir output -p
mkdir output/media -p
mkdir output/media/logo -p

sassc css/main.scss output/main.css

cp template/*.js output/

cp media/logo/*.png output/media/logo/ -r
cp media/background/background.png output/media/background.png
cp media/logo/favicon.ico output/

python3 build.py
