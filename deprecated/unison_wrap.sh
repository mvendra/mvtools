#!/bin/bash

# platform paths
LOCALPATH=/home/user/platform
REMOTEPATH=/home/user/externalmedia

# local sources
SYNCARTIFACTS=(
        Dev
        Music
        Graphics
        )

# errorcode interface
INVALID_SRC=1
INVALID_BOOTSTRAP_DEST=2

function bootstrap(){

  # param1: local source
  # param2: dest (where to do a full copy to)

  mkdir $LOCALPATH
  if (( $? > 0 )); then
    # extra caution
    echo "Local path already exists. Aborting."
    exit $INVALID_BOOTSTRAP_DEST
  fi
  cp -R $REMOTEPATH/* $LOCALPATH

}

function unisonate(){

  # param1: local source
  # param2: dest (where to unison to)
  for tg in ${SYNCARTIFACTS[@]}; do
    loc_tg=$LOCALPATH/$tg
    if [ ! -d $loc_tg ]; then
      echo "Source $loc_tg does not exist."
      exit $INVALID_SRC
    else
      unison $LOCALPATH/$tg $REMOTEPATH/$tg
    fi
  done

}

# lets decide which functionality
if [[ $1 == "bootstrap" ]]; then

  # boostrap on this computer
  if [ -d $LOCALPATH ]; then
    echo "Requested a bootstrap operation but $LOCALPATH is not empty."
    exit $INVALID_BOOTSTRAP_DEST
  fi
  bootstrap

else 
  # sync to previously configured locations
  unisonate
fi
