#!/bin/bash

PWD_FIX=(`pwd -P`)
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
    inline_echo.py $PWD_FIX | xclip -sel clip
elif [[ "$unamestr" == 'Darwin' ]]; then
    inline_echo.py $PWD_FIX | pbcopy
elif [[ "$unamestr" == 'CYGWIN_NT-10.0' ]]; then
	inline_echo.py $PWD_FIX | clip
fi
