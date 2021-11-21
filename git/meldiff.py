#!/usr/bin/env python3

import sys
import os

import generic_run

if __name__ == "__main__":
    if (len(sys.argv) < 8):
        print("This script is not intended for standalone use - integrate with meld instead.")
        sys.exit(1)
    v, r = generic_run.run_cmd_simple(["meld", sys.argv[2], sys.argv[5]])
    if not v:
        print(r)
        sys.exit(1)
