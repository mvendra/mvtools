#!/bin/sh

HTMLBOOTFILE=testforecho.html
if [ ! -z $1 ]; then
  HTMLBOOTFILE=$1
fi

if [ -e ./$HTMLBOOTFILE ]; then
  echo "There's already a ./$HTMLBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$HTMLBOOTFILE

echo "<html>\n  <head>\n    <title>\n      Title\n    </title>\n  </head>\n  <body>\n    Test For Echo\n  </body>\n</html>" > ./$HTMLBOOTFILE

