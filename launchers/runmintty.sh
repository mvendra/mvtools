#!/bin/bash

CMD="$1"
TOOLBUS_SIGNAME="runmintty_result_${BASHPID}"
CMD_FINAL="runmintty_adapter.sh $CMD $TOOLBUS_SIGNAME"

# test if the toolbus signal is clear
toolbus.py --get-signal "$TOOLBUS_SIGNAME" 1>/dev/null # under normal conditions, this results in an error message on stdout so we can suppress it
TOOLBUS_GETSIG_RET=$?

if [ $TOOLBUS_GETSIG_RET -eq 0 ]; then
    echo "Unable to continue with the execution of [$CMD] - the Toolbus signal [$TOOLBUS_SIGNAME] is already in use." >&2
    exit 1
fi

mintty.exe "$CMD_FINAL"

TOOLBUS_SIGVAL=$(toolbus.py --get-signal "$TOOLBUS_SIGNAME")
TOOLBUS_GETSIG_RET=$?

if [ ! $TOOLBUS_GETSIG_RET -eq 0 ]; then
    echo "Unable to get the result of the command [$CMD] - the Toolbus signal [$TOOLBUS_SIGNAME] can't be retrieved." >&2
    exit 1
fi

exit $TOOLBUS_SIGVAL
