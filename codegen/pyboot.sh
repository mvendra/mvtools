#!/bin/sh

SHBOOTFILE=testforecho.py
if [ ! -z $1 ]; then
  SHBOOTFILE=$1
fi

if [ -e ./$SHBOOTFILE ]; then
  echo "There's already a ./$SHBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$SHBOOTFILE
echo "#!/usr/bin/env python\n\nimport sys\nimport os\n\ndef puaq():\n    print(\"Usage: %s params\" % os.path.basename(__file__))\n    sys.exit(1)\n\nif __name__ == \"__main__\":\n\n    if len(sys.argv) < 2:\n        puaq()\n    print(\"elo\")\n" > ./$SHBOOTFILE
chmod +x ./$SHBOOTFILE

