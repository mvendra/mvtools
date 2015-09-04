#!/bin/sh

MKFILEBOOTFILE=Makefile
if [ ! -z $1 ]; then
  MKFILEBOOTFILE=$1
fi

if [ -e ./$MKFILEBOOTFILE ]; then
  echo "There's already a ./$MKFILEBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$MKFILEBOOTFILE
cat $BUILDING/makefiletemplates/Makefile_singlefolder_apponly > ./$MKFILEBOOTFILE

