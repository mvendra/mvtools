#!/bin/bash

# borrowed from https://superuser.com/questions/125376/how-do-i-compare-binary-files-in-linux

function puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` file1 file2"
    if [ "$1" = true ]; then
        exit 0
    else
        exit 1
    fi
}

if [ -z "$1" ]; then
    puaq
fi

if [ -z "$2" ]; then
    puaq false
fi

cmp -l "$1" "$2" | gawk '{printf "%08X %02X %02X\n", $1, strtonum(0$2), strtonum(0$3)}'
