#!/bin/sh

MKFILEBOOTFILE=Makefile
if [ ! -z $1 ]; then
  MKFILEBOOTFILE=$1
fi

if [ -e ./$MKFILEBOOTFILE ]; then
  echo "There's already a ./$MKFILEBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

MKFILE_TEMPLATE=$MVTOOLS/codegen/templates/makefiles/c/Makefile_c_singlefolder_apponly
if [ ! -e $MKFILE_TEMPLATE ]; then
  echo "The makefile template $MKFILE_TEMPLATE does not exist. This script has no hope to succeed."
  exit 1
fi

touch ./$MKFILEBOOTFILE
cat $MKFILE_TEMPLATE > ./$MKFILEBOOTFILE

