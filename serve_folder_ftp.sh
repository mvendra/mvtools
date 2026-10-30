#!/usr/bin/env bash

if [ -z "$1" ]; then
    TG=("`pwd -P`")
else
    TG="$1"
fi

PORT=2121

"$MVTOOLS_PIP_VENV_INSTALL_PATH/bin/python" -m pyftpdlib --directory="$TG" --port="$PORT" --write
