#!/usr/bin/env python3

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(plugins_params, filename, shared_state, num_lines):

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    warn_no_suffix = "lint-c-integer-suffix-warn-no-suffix" in plugins_params
    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    valid_suffixes = ["ll", "ull", "u", "f"]

    corrected_line = ""
    parsing_number = False
    hex_candidate = False
    bin_candidate = False
    parsing_hex = False
    parsing_fp = False
    number_is_fp = False
    parsing_suffix = False
    mod_flag = False

    for idx in range(len(content_line_local)):

        c = content_line_local[idx]

        if parsing_number:

            if hex_candidate or bin_candidate:

                hex_candidate = False
                bin_candidate = False

                if c == "x" or c == "X":
                    parsing_hex = True
                    corrected_line += c
                    continue

                if c == "b" or c == "B":
                    corrected_line += c
                    continue

            if parsing_hex:
                if string_utils.is_hex_string(c):
                    corrected_line += c
                    continue

            if not parsing_fp:
                if c == ".":
                    parsing_fp = True
                    number_is_fp = True
                    corrected_line += c
                    continue

            if string_utils.is_dec_string(c):
                corrected_line += c
                continue

            # integer already ended here - its the suffix's turn
            parsing_suffix = True
            parsing_number = False
            parsing_hex = False
            parsing_fp = False

        else:

            corrected_line += c

            if c == "0":
                parsing_number = True
                hex_candidate = True
                bin_candidate = True
                continue

            if string_utils.is_dec_string(c):
                parsing_number = True
                continue

    # mvtodo: leftover flags?

    if mod_flag:
        return True, ("line [%s] has integer suffix violations" % line_index, [(line_index, corrected_line)])
    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
