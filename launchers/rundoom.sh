#!/bin/bash

function puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` FILE.WAD"
    if [ "$1" = true ]; then
        exit 0
    else
        exit 1
    fi
}

if [ -z $1 ]; then
    puaq false
fi

chocolate-doom -file ./$1
