#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` \"09:00:00\" (e.g. for 9am)"
  exit 1
}

if [ -z $1 ]; then
  puaq
fi

TIMETOSET=$1

date +%T -s $TIMETOSET

