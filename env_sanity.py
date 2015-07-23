#!/usr/bin/env python

""" Attempts to check the sanity of your environment """

import os

if __name__ == "__main__":
    for i in os.environ:
        print(os.environ[i])

