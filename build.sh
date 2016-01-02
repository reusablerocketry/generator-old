#!/bin/sh

mkdir output -p
rm output/* -rf

scss --sourcemap=none css/main.scss output/main.css

mkdir output/media
mkdir output/media/logo

cp media/logo/*.png output/media/logo/ -r
cp media/background/background.png output/media/background.png
cp media/logo/favicon.ico output/

./generate.py
