#!/bin/sh

#rm output/* -rf
mkdir output

scss css/main.scss output/main.css

cp media output/ -r

./generate.py
