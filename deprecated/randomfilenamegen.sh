#!/bin/bash

SHA_APP=""

unamestr=`uname -s`
if [[ "$unamestr" == "Linux" ]]; then
    SHA_APP="sha256sum"
else
    SHA_APP="shasum -a 256"
fi

# first method
RFN=(`date +%s | $SHA_APP | base64 | head -c 48`)
RFN=${RFN}.tmp

if [ -e $RFN ]; then
  echo "Temporary file $RFN already exists! Race hazard is abound. Aborting."
  exit 1
fi

#echo $RFN
inline_echo.py $RFN

# second method
#cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32
