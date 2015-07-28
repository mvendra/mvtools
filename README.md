
MVTOOLS
=======

A collection of tools.

Installation
============

1) Clone the repo somewhere in your system

2) Add: ```export MVTOOLS=/path/to/mvtools``` to your ~/.bashrc

3) Add: ```source $MVTOOLS/mvtools_main.sh``` to your ~/.bashrc

Dependencies
============

The dependencies are optional, depending on which scripts are intended for use.

python

sox

git

openssl

silversearcher-ag

unison

java

meld

xclip

rpm2cpio

autoselfext
===========

Python based creator of self extracting shell scripts

Usage: autoselfext.py input_instructionsfile.sh input_packagefile.tar.gz output_filename.sh

Basically, you create a shell script file (input_instructionsfile.sh) that contains your unpacking code, and a
package of your choice (input_packagefile.tar.gz)

What autoselfext does is join them both inside a self extracting shell script. When called, the resulting shell
script (output_filename.sh) will split up the instructions script and the package file, and then call the instructions
file. In the instructions file, you can unpack your package and install it and etc.

extractbypattern
================

Small app to extract file format patterns from another file. It is by default configured to extract packed (non compressed) png images from another file.

all the rest
============

mvtodo: document the rest

