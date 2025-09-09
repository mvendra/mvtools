#!/bin/bash

TG=("`pwd -P`")
PORT=2121

source "$MVTOOLS_PIP_VENV_INSTALL_PATH/bin/activate"
python -m pyftpdlib --directory="$TG" --port="$PORT" --write
deactivate
