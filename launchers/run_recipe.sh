#!/bin/bash

RECIPE_FILE="$1"

recipe_processor.py --run "$RECIPE_FILE" "${@:2}"
