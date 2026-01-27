#!/bin/bash

unamestr=`uname` # a bit at odds with mvtools's get_platform.py but trying to invoke python from here has caused headaches in the past (msys2)
if [[ ${unamestr:0:5} == "Linux" || ${unamestr:0:9} == "CYGWIN_NT" || ${unamestr:0:7} == "MSYS_NT" || ${unamestr:0:10} == "MINGW64_NT" ]]; then
    alias ls="ls --color --group-directories-first --sort=extension"
fi

alias la="ls -la"
alias lal="ls -1Ap"
alias lash="ls -lash"
alias mv="mv -i"
alias cp="cp -i"
