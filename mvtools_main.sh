#!/bin/bash

add2path(){
  PATH=${PATH}:${1}
}

# this requires the MVTOOLS envvar to be defined somewhere else (.bashrc, likely).

if [[ ! -z $MVTOOLS && -d $MVTOOLS ]]; then

  add2path $MVTOOLS
  add2path $MVTOOLS/audio
  add2path $MVTOOLS/git
  add2path $MVTOOLS/inputfixes
  add2path $MVTOOLS/startservices
  add2path $MVTOOLS/codegen
  add2path $MVTOOLS/security

  # for a nuclear-recursive solution, use this:
  #PATH=${PATH}:$(find ~/the_base_path -type d | tr '\n' ':' | sed 's/:$//')

  # it is preferrable to source other scripts last, because any of their contents may depend on previously added paths
  source $MVTOOLS/git/git_aliases.sh

else
  echo "WARNING: MVTOOLS envvar incorrectly defined. Check your ~/.bashrc"
fi

