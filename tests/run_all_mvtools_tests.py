#!/usr/bin/env python3

import sys
import os

import detect_py_uts
import launch_list

def run_all_mvtools_tests():
    mvtools_tests_path = os.path.dirname(os.path.realpath(__file__))
    uts_list = detect_py_uts.detect_py_uts(mvtools_tests_path)
    v, r = launch_list.run_list(uts_list, None)
    launch_list.print_report(v, r)

if __name__ == "__main__":
    # this script does the equivalent of bash's launch_list.py --nocwd `detect_py_uts.py $PWD`
    # with the advantage of not requirint the cwd to be equal to this script's base path
    run_all_mvtools_tests()