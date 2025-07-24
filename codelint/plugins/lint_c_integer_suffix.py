#!/usr/bin/env python3

import sys
import os

import path_utils
import string_utils

def scan_largest_of(target_str, target_str_offset, source_str_list):

    largest_found = 0
    largest_available = 0
    map_src_offsets = {}

    for e in source_str_list:
        map_src_offsets[e] = 0
        if len(e) > largest_available:
            largest_available = len(e)

    scan_count = 0
    for idx in range(target_str_offset, len(target_str)):
        scan_count += 1

        c = target_str[idx]

        no_matches = True
        for e in source_str_list:

            if scan_count > len(e):
                continue

            if c == e[map_src_offsets[e]]:
                map_src_offsets[e] += 1
                no_matches = False
            else:
                map_src_offsets[e] = 0

            if map_src_offsets[e] == len(e):
                if len(e) > largest_found:
                    largest_found = len(e)

        if no_matches:
            break

        if largest_found == largest_available:
            break

    return largest_found

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
    parsing_suffix = False
    mod_flag = False
    skip_amt = 0

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
                    corrected_line += c
                    continue

            if string_utils.is_dec_string(c):
                corrected_line += c
                continue

            # integer already ended here - its the suffix's turn
            parsing_number = False
            parsing_hex = False
            parsing_fp = False # mvtodo: might need to be used first

            # mvtodo: now its either a matter of knowing which suffixes are bad, or what followup chars are not bad suffixes but something esle (that is also valid)

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
