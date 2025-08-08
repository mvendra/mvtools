#!/bin/bash

INFILE=$1
OUTFILE=$2
PASSPHRASE=$3

function puaq(){ # puaq stands for Print Usage And Quit
    echo "Usage: `basename $0` infile [outfile] [passphrase]"
    exit 1
}

if [ -z $INFILE ]; then
    puaq
fi

if [ ! -e $INFILE ]; then
    echo "Input file $INFILE does not exit. Aborting."
    exit 1
fi

if [ -z $OUTFILE ]; then
    OUTFILE=${INFILE}.enc
fi

if [ -e $OUTFILE ]; then
    echo "$OUTFILE already exists. Will not overwrite. Aborting."
    exit 1
fi

if [ -z $PASSPHRASE ]; then
    echo "Input passphrase..."
    read -s PASSPHRASE
fi

openssl des3 -e -salt -in $INFILE -out $OUTFILE -k $PASSPHRASE
