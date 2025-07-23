#!/usr/bin/env python3

import sys
import os

def line_list_to_string(str_list):

    if not isinstance(str_list, list):
        return None

    idx = 0
    result_str = ""
    list_size = len(str_list)

    for l in str_list:
        idx += 1

        if not isinstance(l, str):
            return None

        result_str += "%s" % l
        if idx < list_size:
            result_str += "\n"

    return result_str

def generic_parse(str_line, separator):
    if str_line is None:
        return None
    if separator is None:
        return None
    n = str_line.find(separator)
    if n == -1:
        return None
    return str_line[:n]

def rfind_first_of(string_source, list_source):

    if string_source is None:
        return None
    if list_source is None:
        return None
    if len(string_source) == 0:
        return None
    if len(list_source) == 0:
        return None
    if not isinstance(list_source, list):
        return None

    last_found = None
    last_found_index = None
    for ls in list_source:
        n = string_source.rfind(ls)
        if n == -1:
            continue
        if last_found_index is None:
            last_found = ls
            last_found_index = n
            continue
        if n > last_found_index:
            last_found = ls
            last_found_index = n

    return (last_found_index, last_found)

def count_any_of(string_source, list_source):

    # will string-count any of list_source. returns the biggest count of any.

    if string_source is None:
        return None
    if list_source is None:
        return None
    if len(string_source) == 0:
        return None
    if len(list_source) == 0:
        return None
    if not isinstance(list_source, list):
        return None

    last_count = None
    for ls in list_source:
        n = string_source.count(ls)
        if last_count is None:
            last_count = n
            continue
        if n > last_count:
            last_count = n

    return last_count

def convert_dos_to_unix(string_source):

    if string_source is None:
        return None

    output_string = ""

    output_string = string_source.replace("\r\n", "\n")

    return output_string

def is_hex_string(the_string):
    try:
        f = int(the_string, 16)
        return True
    except:
        return False

def is_dec_string(the_string):
    try:
        f = int(the_string, 10)
        return True
    except:
        return False

def is_asc_char_string(the_string):

    if the_string is None:
        return False

    if the_string == "":
        return False

    valid_chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    for c in the_string:
        if not c in valid_chars:
            return False
    return True
