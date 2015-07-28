#!/bin/bash

PWD_FIX=(`pwd -P`)
inline_echo.py $PWD_FIX | xclip -sel clip

