#!/usr/bin/env python

""" Attempts to check the sanity of your environment """

import os

if __name__ == "__main__":
  for i in os.environ.keys():
    # mvtodo: check duplicate paths
    # mvtodo: check whether envvar pointing to paths are actually valid paths (path starts with / at least. must have two
    #print(os.environ[i])

