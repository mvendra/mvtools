#!/usr/bin/env python3

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(plugins_params, filename, shared_state, num_lines):

    if "lint-c-integer-suffix-internal-slash-asterisk-state" in shared_state:
        return False, "shared state already contains {lint-c-integer-suffix-internal-slash-asterisk-state}"
    shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    warn_no_suffix = "lint-c-integer-suffix-warn-no-suffix" in plugins_params
    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    min_line_index = 1
    if "lint-c-integer-suffix-min-line" in plugins_params:
        min_line_index = plugins_params["lint-c-integer-suffix-min-line"]

    if not line_index >= min_line_index:
        return True, None

    valid_suffixes_floats = ["f"]
    valid_suffixes_ints = ["ll", "ull", "u"]

    corrected_line = ""
    current_suffix = ""
    closing_sa_comment_candidate = False
    parsing_ds_comment = False # ds = double-slash
    parsing_comment_candidate = False
    parsing_var = False
    parsing_char = 0
    parsing_str = False
    parsing_str_esc_flag = False
    parsing_number = False
    hex_candidate = False
    bin_candidate = False
    parsing_hex = False
    parsing_fp = False
    number_was_fp = False
    parsing_suffix = False
    findings = 0

    for idx in range(len(content_line_local)):

        c = content_line_local[idx]

        # skippages (reject false positives)
        if parsing_comment_candidate:

            parsing_comment_candidate = False

            if c == "*":
                shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = True
                corrected_line += c
                continue

            if c == "/":
                parsing_ds_comment = True
                corrected_line += c
                continue

        if closing_sa_comment_candidate:

            closing_sa_comment_candidate = False

            if c == "/":
                shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False
                corrected_line += c
                continue

        if shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"]:

            if c == "*":
                closing_sa_comment_candidate = True

            corrected_line += c
            continue

        if parsing_ds_comment:

            corrected_line += c
            continue

        if parsing_char > 0:

            parsing_char -= 1
            corrected_line += c
            continue

        if parsing_str:

            if c == "\\":
                parsing_str_esc_flag = not parsing_str_esc_flag
            elif c == "\"":
                if not parsing_str_esc_flag:
                   parsing_str = False
            else:
                parsing_str_esc_flag = False

            corrected_line += c
            continue

        if parsing_var:

            if c == "_":
                corrected_line += c
                continue

            if string_utils.is_asc_char_string(c):
                corrected_line += c
                continue

            if string_utils.is_dec_string(c):
                corrected_line += c
                continue

            parsing_var = False

        # suffix
        if parsing_suffix:

            if string_utils.is_asc_char_string(c):
                current_suffix += c
                continue

            # suffix ended (with remaining contents)
            valid_suffixes_local = valid_suffixes_ints
            if number_was_fp:
                valid_suffixes_local = valid_suffixes_floats

            if current_suffix in valid_suffixes_local:
                corrected_line += current_suffix
            else:
                findings += 1 # invalid suffix removed (skipped) from final resulting line

            number_was_fp = False
            parsing_suffix = False
            current_suffix = ""

        # main part - pasing numbers
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
                if string_utils.is_dec_string(c): # a floating-point dot requires a followup decimal number - or else, its something else
                    number_was_fp = True
                else:
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
            number_was_fp = False
            corrected_line += c
            if warn_no_suffix:
                findings += 1

        else: # new parsing

            corrected_line += c

            if c == "/":
                parsing_comment_candidate = True
                continue

            if c == "0":
                parsing_number = True
                hex_candidate = True
                bin_candidate = True
                continue

            if string_utils.is_dec_string(c):
                parsing_number = True
                continue

            if c == "_":
                parsing_var = True
                continue

            if string_utils.is_asc_char_string(c):
                parsing_var = True
                continue

            if c == "\"":
                parsing_str = True
                continue

            if c == "\'":
                parsing_char = 2
                continue

    if parsing_suffix: # suffix ended (end-of-line)

        valid_suffixes_local = valid_suffixes_ints
        if number_was_fp:
            valid_suffixes_local = valid_suffixes_floats

        if current_suffix in valid_suffixes_local:
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
        plural_maybe = ""
        if findings > 1:
            plural_maybe = "s"
        return True, ("[%s:%s] has [%s] integer suffix violation%s." % (filename, line_index, findings, plural_maybe), final_patches)
    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
