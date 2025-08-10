#!/bin/bash

RECIPE_FILE="$1"

recipe_processor.py --test "$RECIPE_FILE" "${@:2}"
