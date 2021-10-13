#!/usr/bin/env python3

import sys
import os

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
