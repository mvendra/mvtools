#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` \"09:00:00\" (e.g. for 9am)"
    if [ "$1" = true ]; then
        exit 0
    else
        exit 1
    fi
}

if [ -z $1 ]; then
    puaq false
fi

TIMETOSET=$1

date +%T -s $TIMETOSET
