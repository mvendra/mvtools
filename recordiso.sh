#!/bin/bash

function puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` isoimage.iso"
    if [ "$1" = true ]; then
        exit 0
    else
        exit 1
    fi
}

if [ -z $1 ]; then
    puaq false
fi

DEVICEFILE=/dev/sr0 # mvtodo: detect the system's device file (create another script for that!)
IMAGEFILE=$1

if [ ! -f $IMAGEFILE ]; then
    echo "$IMAGEFILE does not exist. Aborted."
    exit 2
fi

cdrecord -v -dao dev=$DEVICEFILE $IMAGEFILE
