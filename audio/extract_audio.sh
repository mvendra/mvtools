#!/bin/bash

if [ -z $1 ]; then
  echo "Missing input file"
  exit 1
fi

if [ -z $2 ]; then
  echo "Missing output file"
  exit 2
fi

ffmpeg -i $1 -vn -acodec mp3 $2
