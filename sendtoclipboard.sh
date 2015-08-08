#!/bin/bash

puaq(){ # puaq stands for Print Usage And Quit
  echo "Usage: `basename $0` contents"
  exit 1
}

CONTENTS=$1

if [ -z $CONTENTS ]; then
  puaq
fi

inline_echo.py $CONTENTS | xclip -sel clip

