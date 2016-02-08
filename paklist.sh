#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` [--hash] package_file"
  exit 1
}

# testing input params
if [ -z $1 ]; then
  puaq
fi

FILENAME=$1

EXTENSION="${FILENAME##*.}"

if [ $EXTENSION == "zip" ]; then
  unzip -l ./$FILENAME
elif [ $EXTENSION == "tar" ] || [ $EXTENSION == "gz" ] || [ $EXTENSION == "bz2" ]; then
  tar -tf ./$FILENAME
fi

