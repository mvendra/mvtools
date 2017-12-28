#!/bin/sh

PYBOOTFILE=testforecho.py
if [ ! -z $1 ]; then
  PYBOOTFILE=$1
fi

if [ -e ./$PYBOOTFILE ]; then
  echo "There's already a ./$PYBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$PYBOOTFILE
echo "#!/usr/bin/env python3\n\nimport sys\nimport os\n\ndef puaq():\n    print(\"Usage: %s params\" % os.path.basename(__file__))\n    sys.exit(1)\n\nif __name__ == \"__main__\":\n\n    if len(sys.argv) < 2:\n        puaq()\n    print(\"elo\")\n" > ./$PYBOOTFILE
chmod +x ./$PYBOOTFILE

