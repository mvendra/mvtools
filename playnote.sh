#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` note. Examples: C1, C#4, A3, B2"
  exit 1
}

if [ -z $1 ]; then
  puaq
fi

play -qn synth 2 pluck $1 &

