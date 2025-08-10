#!/bin/bash

echo "Currently disabled! This script has a bug: It attaches itself to the first terminal it knows of (by pid probably). This fails when using multiple terminals in different workspaces."
exit

TERMINAL="xfce4-terminal"
TITLE="$1"
COMMAND="$2"
WORKDIR=("`pwd -P`")

if [ ! -z "$3" ]; then
    WORKDIR="$3"
fi

if [ -z "$COMMAND" ]; then
    COMMAND="ls"
fi

$TERMINAL --tab --working-directory="$WORKDIR" -T "$TITLE" -e 'bash -ic "'$COMMAND'; exec bash"'
