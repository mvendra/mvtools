#!/bin/bash

CMD=$1

rm ~/nuke/last_run # mvtodo: in the future, should use the toolbus instead
$CMD
echo $? > ~/nuke/last_run # mvtodo: in the future, should use the toolbus instead
