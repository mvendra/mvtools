#!/bin/sh

JAVABOOTFILE=Main.java
if [ ! -z $1 ]; then
  JAVABOOTFILE=$1
fi

if [ -e ./$JAVABOOTFILE ]; then
  echo "There's already a ./$JAVABOOTFILE in the CWD (`pwd -P`), so this script is aborted."
  exit 1
fi

touch ./$JAVABOOTFILE
echo "\npackage pak;\n\npublic class Main {\n\n    public static void main(String[] args){\n        System.out.println(\"test for echo\");\n    }\n}\n" > ./$JAVABOOTFILE

