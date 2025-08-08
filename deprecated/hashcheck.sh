#!/bin/bash

function puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` archive-to-check"
    exit 1
}

if [ -z $1 ]; then
    puaq
fi

if [ ! -f $1 ]; then
    echo "$1 does not exist."
    exit 2
fi

HASHFNAME=$1.sha256

if [ ! -f $HASHFNAME ]; then
    echo "ERROR: $HASHFNAME is not present. Aborting"
    exit 3
fi

TMPFNAME=(`randomfilenamegen.sh`)
TMPFNAME=${TMPFNAME}.tmpfile

if [ -e $TMPFNAME ]; then
    echo "ERROR: Temporary filename $TMPFNAME conflict! Aborting."
    exit 4
fi

sha256sum $1 > $TMPFNAME
diff $HASHFNAME $TMPFNAME 

if [ $? -eq 0 ]; then
    echo "Match!"
else
    echo "No match"
fi

if [ ! -z $TMPFNAME ]; then
    rm $TMPFNAME
fi
