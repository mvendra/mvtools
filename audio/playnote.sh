#!/bin/bash

function puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` note. Examples: C1, C#4, A3, B2"
    if [ "$1" = true ]; then
        exit 0
    else
        exit 1
    fi
}

if [ -z "$1" ]; then
    puaq false
fi

play -qn synth 2 pluck "$1" &
