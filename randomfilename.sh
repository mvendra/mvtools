#!/bin/bash

# first method
date +%s | sha256sum | base64 | head -c 32 ; echo

# second method
#cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32

