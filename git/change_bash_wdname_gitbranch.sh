#!/bin/bash

# shell colors
export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagacad

# git branch display
function proml(){
    local        BLUE="\[\033[0;34m\]"
    local         RED="\[\033[0;31m\]"
    local   LIGHT_RED="\[\033[1;31m\]"
    local       GREEN="\[\033[0;32m\]"
    local LIGHT_GREEN="\[\033[1;32m\]"
    local       YELLOW="\[\033[0;33m\]"
    local       WHITE="\[\033[1;37m\]"
    local  LIGHT_GRAY="\[\033[0;37m\]"
    local        GRAY="\[\033[1;30m\]"
    local       RESET="\[\033[0m\]"
    export PS1="$RESET\u@\h:\w$GREEN\$(parse_git_branch)$RESET$ "
}

function parse_git_branch(){
    git branch --no-color 2> /dev/null | sed -e "/^[^*]/d" -e "s/* \(.*\)/(\1)/"
}
