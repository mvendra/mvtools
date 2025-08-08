#!/bin/bash

deploy_lib(){
    mkdir_if_needed_and_possible.sh $4
    rm -rf $4/$3
    export $1=$4
    run_recipe.sh $2
    if [ $? != 0 ]; then
        exit 1
    fi
}
