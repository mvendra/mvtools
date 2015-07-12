#!/usr/bin/env python

import sys
import os

result=os.sep
for args in sys.argv[1:]:
  result+=args+os.sep
print(result)

