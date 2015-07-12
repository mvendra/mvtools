#!/bin/bash

if [ -z $1 ]; then
  echo "oh long johnson"
  exit 1
fi

rpm2cpio $1 | cpio -id

