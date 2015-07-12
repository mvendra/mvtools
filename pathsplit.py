#!/usr/bin/env python

import sys

def explodepath(apath):
  tokens = apath.split("/")
  result=""
  for tk in tokens:
    if tk == "":
      continue
    else:
      result+=tk+" "

  result=result[:len(result)-1] # removes trailing blank space
  return result

for arg in sys.argv[1:]:
  ret=explodepath(arg)
  print(ret)

