#!/bin/sh

SHBOOTFILE=testforecho.html
if [ ! -z $1 ]; then
  SHBOOTFILE=$1
fi

if [ -e ./$SHBOOTFILE ]; then
  echo "There's already a ./$SHBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$SHBOOTFILE

echo "<html>\n  <head>\n    <title>\n      Title\n    </title>\n  </head>\n  <body>\n    Test For Echo\n  </body>\n</html>" > ./$SHBOOTFILE
chmod +x ./$SHBOOTFILE

