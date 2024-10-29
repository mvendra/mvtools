#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` path"
    exit 1
}

if [ -z $1 ]; then
    puaq
fi

TARGET_PATH=$1

if [ ! -e $TARGET_PATH ]; then
    mkdir $TARGET_PATH
fi
