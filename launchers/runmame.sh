#!/bin/bash

ROM="$1"
DEBUG=""
SYSTEM="genesis"

if [ "$1" = "debug" ]; then
    DEBUG="-debug"
    ROM="$2"
else
    ROM="$1"
fi

mame $SYSTEM $DEBUG -window -cart "$ROM"
