#!/bin/bash

function quit_fail_any_err(){
    if [ "$1" != "0" ]; then
        exit 1
    fi
}

function quit_ok_if_defined(){
    if [ ! -z "$1" ]; then
        exit 0
    fi
}

function quit_combo(){
    quit_fail_any_err "$1"
    quit_ok_if_defined "$2"
}

function deploy_lib(){
    mkdir_if_needed_and_possible.sh "$4"
    rm -rf "$4/$3"
    export "$1"="$4"
    run_recipe.sh "$2"
    recipe_ret="$?"
    echo ""
    quit_fail_any_err "$recipe_ret"
}
