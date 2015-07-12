#!/bin/sh

SHBOOTFILE=testforecho.py
if [ ! -z $1 ]; then
  SHBOOTFILE=$1
fi

if [ -f ./$SHBOOTFILE ]; then
  echo "There's already a ./$SHBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$SHBOOTFILE
echo "#!/usr/bin/env python\n\nif __name__ == \"__main__\":\n  print(\"elo\")\n" > ./$SHBOOTFILE
chmod +x ./$SHBOOTFILE

