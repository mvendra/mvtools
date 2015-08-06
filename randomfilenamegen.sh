#!/bin/bash

# first method
RFN=(`date +%s | sha256sum | base64 | head -c 48`)
RFN=${RFN}.tmp

if [ -e $RFN ]; then
  echo "Temporary file $RFN already exists! Race hazard is abound. Aborting."
  exit 1
fi

#echo $RFN
inline_echo.py $RFN

# second method
#cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32

