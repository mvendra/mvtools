#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` folder"
  exit 1
}

TARGET_DIR=$1

if [ -z $TARGET_DIR ]; then
  puaq
fi

if [ ! -d $TARGET_DIR ]; then
  echo "$TARGET_DIR does not exist or is not a directory"
fi

# resolve symlinks
cd $TARGET_DIR
TARGET_DIR=`pwd -P`

du -h $TARGET_DIR | tail -n 1

