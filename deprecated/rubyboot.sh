#!/bin/sh

RUBYBOOTFILE="testforecho.rb"
if [ ! -z "$1" ]; then
    RUBYBOOTFILE="$1"
fi

if [ -e "./$RUBYBOOTFILE" ]; then
    echo "There's already a ./$RUBYBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
    exit 1
fi

touch "./$RUBYBOOTFILE"
echo "#!/usr/bin/ruby\n\nputs 'hello world'\n" > "./$RUBYBOOTFILE"
chmod +x "./$RUBYBOOTFILE"
