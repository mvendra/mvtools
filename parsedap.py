#!/usr/bin/env python

# Parse Device Accel Profile

import re
import sys
import os

if (len(sys.argv) > 1):
  STR=" ".join(sys.argv[1:])
else:
  STR=sys.stdin.read().strip()

m = re.search("Device Accel Profile ([0-9]+):", STR)
if m == None:
  print("")
  sys.exit(1)

m = re.search("[0-9]+", m.group(0))
if m == None:
  print("")
  sys.exit(1)

print(m.group(0))

