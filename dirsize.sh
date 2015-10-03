#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` folder"
  exit 1
}

TARGET_DIR=${@}
TARGET_DIR=`resolve_and_escape_path.py $TARGET_DIR`

# resolve symlinks
cd $TARGET_DIR
TARGET_DIR=`pwd -P`

if [ -z $TARGET_DIR ]; then
  puaq
fi

if [ ! -d $TARGET_DIR ]; then
  echo "$TARGET_DIR does not exist or is not a directory"
fi

du -h $TARGET_DIR | tail -n 1

