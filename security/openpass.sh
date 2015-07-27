#!/bin/bash

INFILE=$1

if [ -z $INFILE ]; then
  echo "Missing input file"
  exit 1
fi

echo "Input..."
read -s PASS

RANDOM_FN_TMP=(`randomfilenamegen.sh`)

if [ -z $RANDOM_FN_TMP ]; then
  echo "Cannot generate random file name for aux temp. Aborting."
  exit 1
fi

openssl des3 -d -salt -in $INFILE -out $RANDOM_FN_TMP -k $PASS
LASTBYTE=(`xxd -p -s -1 $RANDOM_FN_TMP`)
if [ $LASTBYTE == "0a" ]; then
  truncate -s -1 $RANDOM_FN_TMP # removes the trailing 0a (\n)
fi

cat $RANDOM_FN_TMP | xclip -sel clip
rm $RANDOM_FN_TMP

