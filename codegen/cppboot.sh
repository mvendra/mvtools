#!/bin/sh

CPPBOOTFILE=main.cpp
if [ ! -z $1 ]; then
  CPPBOOTFILE=$1
fi

if [ -e ./$CPPBOOTFILE ]; then
  echo "There's already a ./$CPPBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$CPPBOOTFILE
echo "\n#include <iostream>\n\nint main(int argc, char *argv[]){\n\n    std::cout << \"test for echo\" << std::endl;\n\n    return 0;\n\n}" > ./$CPPBOOTFILE

