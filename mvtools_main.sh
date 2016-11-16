#!/bin/bash

add2path(){

  unamestr=`uname`
  if [[ ! $unamestr == "CYGWIN_NT-10.0" ]]; then
      if [ -z $PATH ]; then
        # first use. dont add the comma at the beginning
        export PATH=${1}
        return
      fi
  fi

  export PATH=${PATH}:${1}

}

add2pythonpath(){
  if [ -z $PYTHONPATH ]; then
    # first use. dont add the comma at the beginning
    export PYTHONPATH=${1}
  else
    export PYTHONPATH=${PYTHONPATH}:${1}
  fi
}

# this requires the MVTOOLS envvar to be defined somewhere else (.bashrc, likely).

if [[ ! -z $MVTOOLS && -d $MVTOOLS ]]; then

  add2path $MVTOOLS
  add2pythonpath $MVTOOLS

  add2path $MVTOOLS/audio
  add2pythonpath $MVTOOLS/audio

  add2path $MVTOOLS/git
  add2path $MVTOOLS/git/visitor
  add2path $MVTOOLS/git/visitor/interfaces
  add2path $MVTOOLS/git/visitor/backends
  add2pythonpath $MVTOOLS/git
  add2pythonpath $MVTOOLS/git/visitor
  add2pythonpath $MVTOOLS/git/visitor/interfaces
  add2pythonpath $MVTOOLS/git/visitor/backends

  add2path $MVTOOLS/inputfixes
  add2pythonpath $MVTOOLS/inputfixes

  add2path $MVTOOLS/codegen
  add2pythonpath $MVTOOLS/codegen

  add2path $MVTOOLS/security
  add2pythonpath $MVTOOLS/security

  add2path $MVTOOLS/startservices

  # for a nuclear-recursive solution, use this:
  #PATH=${PATH}:$(find ~/the_base_path -type d | tr '\n' ':' | sed 's/:$//')

  # coreutils customisations
  source $MVTOOLS/coreutils_custom.sh

  # it is preferrable to source other scripts last, because any of their contents may depend on previously added paths
  source $MVTOOLS/git/git_aliases.sh

else
  echo "WARNING: MVTOOLS envvar incorrectly defined. Check your ~/.bashrc"
fi

