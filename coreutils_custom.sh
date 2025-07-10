#!/bin/bash

platform=`get_platform.py`
if [[ "$platform" == "linux" ]]; then
    alias ls="ls --color --group-directories-first --sort=extension"
fi

alias la="ls -la"
alias lal="ls -1Ap"
alias lash="ls -lash"
alias mv="mv -i"
alias cp="cp -i"
