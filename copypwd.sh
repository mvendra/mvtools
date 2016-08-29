#!/bin/bash

PWD_FIX=(`pwd -P`)
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
    inline_echo.py $PWD_FIX | xclip -sel clip
else
    inline_echo.py $PWD_FIX | pbcopy
fi

