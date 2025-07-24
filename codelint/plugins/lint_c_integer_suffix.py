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
    current_suffix = ""
    parsing_number = False
    hex_candidate = False
    bin_candidate = False
    parsing_hex = False
    parsing_fp = False
    parsing_suffix = False
    findings = 0

    for idx in range(len(content_line_local)):

        c = content_line_local[idx]

        if parsing_suffix:

            if string_utils.is_asc_char_string(c):
                current_suffix += c
                continue

            # suffix ended (with remaining contents)
            if current_suffix in valid_suffixes:
                corrected_line += current_suffix
            else:
                findings += 1 # invalid suffix removed (skipped) from final resulting line

            parsing_suffix = False
            current_suffix = ""

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

            if parsing_fp:
                parsing_fp = False
                if not string_utils.is_dec_string(c): # a floating-point dot requires a followup decimal number - or else, its something else
                    parsing_number = False
                    corrected_line += c
                    continue

            if c == ".":
                parsing_fp = True
                corrected_line += c
                continue

            if parsing_hex:
                if string_utils.is_hex_string(c):
                    corrected_line += c
                    continue

            if string_utils.is_dec_string(c):
                corrected_line += c
                continue

            # integer already ended here
            parsing_number = False
            parsing_hex = False

            # it might be the beginning of a suffix
            if string_utils.is_asc_char_string(c):
                parsing_suffix = True
                current_suffix += c
                continue

            # its something else
            corrected_line += c
            if warn_no_suffix:
                findings += 1

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

    if parsing_suffix: # suffix ended (end-of-line)
        if current_suffix in valid_suffixes:
            corrected_line += current_suffix
        else:
            findings += 1 # invalid suffix removed (skipped) from final resulting line
    else:
        if parsing_number and warn_no_suffix: # optionally report missing suffix
            findings += 1

    if findings > 0:
        final_patches = []
        if content_line_local != corrected_line: # only report patches if actual modifications are being offered (because suffix-less cases are optional and dont produce patches)
            final_patches = [(line_index, corrected_line)]
        return True, ("line [%s] has [%s] integer suffix violations" % (line_index, findings), final_patches)
    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
