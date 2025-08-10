#!/bin/sh

CBOOTFILE="main.c"
if [ ! -z "$1" ]; then
    CBOOTFILE="$1"
fi

if [ -e "./$CBOOTFILE" ]; then
    echo "There's already a ./$CBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
    exit 1
fi

touch "./$CBOOTFILE"
echo "\n#include <stdio.h>\n\nint main(int argc, char *argv[]){\n\n    (void)argc; (void)argv;\n    printf(\"test for echo\\\n\");\n\n    return 0;\n\n}" > "./$CBOOTFILE"
