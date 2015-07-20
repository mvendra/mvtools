#!/bin/bash

add2path(){
  PATH=${PATH}:${1}
}

# this requires the MVTOOLS envvar to be defined somewhere else. somewhere in your bashrc, likely.

if [[ ! -z $MVTOOLS && -d $MVTOOLS ]]; then

  source $MVTOOLS/git_aliases.sh

  add2path $MVTOOLS
  add2path $MVTOOLS/mousefixes

  # for a nuclear-recursive solution, use this:
  #PATH=${PATH}:$(find ~/the_base_path -type d | tr '\n' ':' | sed 's/:$//')

else
  echo "WARNING: MVTOOLS envvar incorrectly defined. Check your ~/.bashrc"
fi

