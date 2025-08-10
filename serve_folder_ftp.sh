#!/bin/bash

TG=("`pwd -P`")
PORT=2121

# to install the pyftpdlib dependency: pip install --user pyftpdlib
python -m pyftpdlib --directory="$TG" --port="$PORT" --write
