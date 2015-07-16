#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename recordiso.sh` param"
  exit 1
}

if [ -z $1 ]; then
  puaq
fi

#code goes here

