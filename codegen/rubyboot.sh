#!/bin/sh

RBBOOTFILE=testforecho.rb
if [ ! -z $1 ]; then
  RBBOOTFILE=$1
fi

if [ -e ./$RBBOOTFILE ]; then
  echo "There's already a ./$RBBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$RBBOOTFILE
echo "#!/usr/bin/ruby\n\nputs 'hello world'\n" > ./$RBBOOTFILE
chmod +x ./$RBBOOTFILE

