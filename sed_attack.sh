#!/bin/bash

FINDWHAT=$1
CHANGETO=$2

if [[ $FINDWHAT == "" ]] ; then
    echo "Usage: `basename $0` find_what replace_with"
    exit
fi

if [[ $CHANGETO == "" ]]; then
    echo "Usage: `basename $0` find_what replace_with"
    exit
fi

SELF=$PWD/`basename $0`

FILES=`ls -R $PWD | awk '
/:$/&&f{s=$0;f=0}
/:$/&&!f{sub(/:$/,"");s=$0;f=1;next}
NF&&f{ print s"/"$0 }'`

for f in $FILES
do
    if [ -f $f ]; then
        if [ $SELF != $f ]; then
            sed -i "s/$FINDWHAT/$CHANGETO/g" $f
        fi
    fi
done
