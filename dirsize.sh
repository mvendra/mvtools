#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` folder"
  exit 1
}

if [ -z $1 ]; then
  puaq
fi

if [ ! -d $1 ]; then
  echo "$1 does not exist or is not a directory"
fi

du -h ./$1 | tail -n 1

