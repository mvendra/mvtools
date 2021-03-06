#!/bin/bash

# borrowed from https://superuser.com/questions/125376/how-do-i-compare-binary-files-in-linux

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` file1 file2"
  exit 1
}

if [ -z $1 ]; then
  puaq
fi

if [ -z $2 ]; then
  puaq
fi

cmp -l $1 $2 | gawk '{printf "%08X %02X %02X\n", $1, strtonum(0$2), strtonum(0$3)}'
