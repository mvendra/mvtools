#!/usr/bin/env python

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_desc():
    return "checks C source files for proper unsigned integer hexadecimal notation usage"

def lint_pre(plugins_params, filename, shared_state, num_lines):

    if "lint-c-unsigned-integer-hex-internal-slash-asterisk-state" in shared_state:
        return False, "shared state already contains {lint-c-unsigned-integer-hex-internal-slash-asterisk-state}"
    shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    corrected_line = ""
    closing_sa_comment_candidate = False
    parsing_ds_comment = False # ds = double-slash
    parsing_comment_candidate = False
    parsing_var = False
    parsing_char = 0
    parsing_str = False
    parsing_str_esc_flag = False
    parsing_number = False
    hex_candidate = False
    parsing_hex = False
    parsing_hex_found_issue = False
    findings = 0

    for idx in range(len(content_line_local)):

        c = content_line_local[idx]

        # skippages (reject false positives)
        if parsing_comment_candidate:

            parsing_comment_candidate = False

            if c == "*":
                shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = True
                corrected_line += c
                continue

            if c == "/":
                parsing_ds_comment = True
                corrected_line += c
                continue

        if closing_sa_comment_candidate:

            closing_sa_comment_candidate = False

            if c == "/":
                shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False
                corrected_line += c
                continue

        if shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"]:

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

        # main part - parsing numbers
        if parsing_number:

            if hex_candidate:

                hex_candidate = False

                if c == "x" or c == "X":
                    parsing_hex = True
                    corrected_line += c
                    continue

            if parsing_hex:
                if string_utils.is_hex_string(c):
                    if not c.isupper() and not parsing_hex_found_issue:
                        findings += 1
                        parsing_hex_found_issue = True
                    corrected_line += c.upper()
                    continue

            if string_utils.is_dec_string(c):
                corrected_line += c
                continue

            # integer already ended here
            parsing_number = False
            parsing_hex = False
            parsing_hex_found_issue = False

            # its something else
            corrected_line += c

        else: # new parsing

            corrected_line += c

            if c == "/":
                parsing_comment_candidate = True
                continue

            if c == "0":
                parsing_number = True
                hex_candidate = True
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

    if findings > 0:
        final_patches = []
        if content_line_local != corrected_line: # only report patches if actual modifications are being offered
            final_patches = [(line_index, corrected_line)]
        plural_maybe = ""
        if findings > 1:
            plural_maybe = "s"
        return True, ("[%s:%s] has [%s] unsigned integer hexadecimal notation violation%s." % (filename, line_index, findings, plural_maybe), final_patches)
    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
