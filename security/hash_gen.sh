#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` archive-to-hash"
    if [ "$1" = true ]; then
        exit 0
    else
        exit 1
    fi
}

if [ -z $1 ]; then
    puaq false
fi

if [ ! -f $1 ]; then
    echo "$1 does not exist."
    exit 2
fi

HASHFNAME=$1.sha512

if [ -e $HASHFNAME ]; then
    echo "$HASHFNAME exists. Refusing to overwrite."
    exit 3
fi

sha512sum $1 > $HASHFNAME
