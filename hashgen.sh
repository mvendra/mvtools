#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` archive-to-hash"
  exit 1
}

if [ -z $1 ]; then
  puaq
fi

if [ ! -f $1 ]; then
  echo "$1 does not exist."
  exit 2
fi

HASHFNAME=$1.sha256

if [ -e $HASHFNAME ]; then
  echo "$HASHFNAME exists. Refusing to overwrite."
  exit 3
fi

sha256sum $1 > $HASHFNAME

