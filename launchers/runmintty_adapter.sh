#!/bin/bash

CMD=$1
TOOLBUS_SIGNAME=$2

$CMD
RUN_RESULT=$?

# send the result over to the caller via toolbus
toolbus.py --set-signal $TOOLBUS_SIGNAME $RUN_RESULT
TOOLBUS_SETSIG_RET=$?

if [ ! $TOOLBUS_SETSIG_RET -eq 0 ]; then
    echo "Unable to submit command result to Toolbus: the signal [$TOOLBUS_SIGNAME] is already in use." >&2
    exit 1
fi
