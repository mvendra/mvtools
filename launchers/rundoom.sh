#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` FILE.WAD"
  exit 1
}

if [ -z $1 ]; then
  puaq
fi

chocolate-doom -file ./$1

