#!/usr/bin/env python

# this is AGF - AG (the silversearcher), but Filtered

import os
import sys
import filteredfilelister 
from subprocess import check_output

if __name__ == "__main__":
  if len(sys.argv) < 4:
    print("Usage: %s path search extensions " % os.path.basename(__file__))
    sys.exit(1)
  ret = filteredfilelister.makefilelist(sys.argv[1], sys.argv[3:])
  p_res = ""
  for k in ret:
    for r in ret[k]:
      out = check_output(["ag", sys.argv[2], r])
      if not len(out):
        continue
      print("\033[94m%s" % r)
      print("\033[0m%s" % out)

