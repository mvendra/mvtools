#!/bin/bash


# usage: cher what_to_grep | cher what_to_find cpp

if [ -z $1 ]; then 
    echo "No target"
    exit
fi
SUBJ=$1

EXT="*"
if [ ! -z $2 ]; then # has extension parameter as well 
    EXT=$2
fi

egrep --color=always -i --include \*.$EXT -nR "*$SUBJ*" ./

