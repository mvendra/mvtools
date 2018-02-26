#!/bin/bash

DELAY=3 # in seconds
RECORDING_TIME=60 # in seconds
FILENAME="desktop.ogv"

PRE_DETECT=`ps aux | grep recordmydesktop | wc -l`

if [ $PRE_DETECT != "1" ]; then
    echo "recordmydesktop is already running. Aborting."
    exit 1
fi

if [ -f $FILENAME ]; then
    echo "$FILENAME already exists. Aborting."
    exit 2
fi

if [ ! -z $1 ]; then
    RECORDING_TIME=$1
fi

sleep $DELAY

echo "Beginning."
recordmydesktop -o $FILENAME --fps 29 --v_bitrate 2000000 --s_quality 10 &
PID=`ps aux | grep recordmydesktop | awk 'NR==1{print $2}'`
sleep $RECORDING_TIME
kill -15 $PID
echo "Done."
exit
