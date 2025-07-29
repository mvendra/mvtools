#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` path"
    if [ "$1" = true ]; then
        exit 0
    else
        exit 1
    fi
}

if [ -z $1 ]; then
    puaq false
fi

TARGET_PATH=$1

if [ ! -e $TARGET_PATH ]; then
    mkdir $TARGET_PATH
fi
