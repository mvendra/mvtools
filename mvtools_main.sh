#!/bin/bash

add2path(){

    unamestr=`uname`
    if [[ ! ${unamestr:0:9} == "CYGWIN_NT" ]]; then
        if [ -z "$PATH" ]; then
            # first use. dont add the comma at the beginning
            export PATH=${1}
            return
        fi
    fi

    if [[ $PATH =~ $1 ]]; then
        echo "Warning: envvar [$1] is already in the PATH"
        return
    fi

    export PATH=${PATH}:${1}

}

add2pythonpath(){

    if [ -z $PYTHONPATH ]; then
        # first use. dont add the comma at the beginning
        export PYTHONPATH=${1}
    else
        if [[ $PYTHONPATH =~ $1 ]]; then
            echo "Warning: envvar [$1] is already in the PYTHONPATH"
            return
        fi
        export PYTHONPATH=${PYTHONPATH}:${1}
    fi

}

if [ -z $MVTOOLS_LINKS_PATH ]; then
    MVTOOLS_LINKS_PATH=$MVTOOLS/links
fi

# this requires the MVTOOLS envvar to be defined in the environment
if [[ ! -z $MVTOOLS && -d $MVTOOLS ]]; then

    add2path $MVTOOLS_LINKS_PATH
    add2pythonpath $MVTOOLS_LINKS_PATH

    # coreutils customisations
    source $MVTOOLS/coreutils_custom.sh

    # it is preferrable to source other scripts last, because any of their contents may depend on previously added paths
    source $MVTOOLS/git/git_aliases.sh

else
    echo "WARNING: MVTOOLS envvar is defined incorrectly."
fi
