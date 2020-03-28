#!/bin/bash

CMD=$1
CMD_FINAL="runmintty_adapter.sh $CMD"

mintty.exe $CMD_FINAL

LAST_RUN=$(cat ~/nuke/last_run) # mvtodo: in the future, should use the toolbus instead
rm ~/nuke/last_run # mvtodo: in the future, should use the toolbus instead
exit $LAST_RUN
