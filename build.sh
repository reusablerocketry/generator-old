#!/bin/sh

rm build -rf
mkdir build

scss css/main.scss build/main.css

cp media build/ -r

./generate.py
