#!/bin/bash

# this script was deprecated in L24 - pakgen.py should eventually take over the functionality of generating packages of/with multiple formats

function puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` [--hash] file_or_folder"
    exit 1
}

# testing input params
if [ -z $1 ]; then
    puaq
fi

DO_HASH=false
TARGET=""

if [ "$1" == "--hash" ]; then
    DO_HASH=true
    TARGET=$2
else
    TARGET=$1
fi

if [ -z $TARGET ]; then
    puaq
fi

if [[ ! -f $TARGET && ! -d $TARGET ]]; then
    echo "Does $TARGET even exist?"
    exit 2
fi

FILENAME=`basename $TARGET`

zip -r $FILENAME.zip $TARGET

if $DO_HASH; then
    sha512sum $FILENAME.zip > $FILENAME.zip.sha512
fi
