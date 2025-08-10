#!/bin/bash

MYNAME=`basename $0`

if [ -z "$1" ]; then
    echo "Usage: $MYNAME packagename"
    exit 1
fi

dpkg-query -L "$1"
