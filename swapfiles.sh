#!/bin/bash

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

FILE1=$1
FILE2=$2

FILEAUX=`randomfilenamegen.sh`
if [ $? != 0 ]; then
  echo "Random filename generation failed. Aborting..."
  exit 1
fi

mv $FILE1 $FILEAUX
mv $FILE2 $FILE1
mv $FILEAUX $FILE2

