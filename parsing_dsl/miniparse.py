#!/usr/bin/env python

import sys
import os
import re

import path_utils

IDENTIFIER = "[^\\\x00\\\x0a\\\x09\\\x20\\\x5b\\\x5d\\\x7b\\\x7d\\\x28\\\x29\\\x3d\\\x2f\\\x5c\\\x24\\\x7e\\\x40\\\x22\\\x3a\\\x3b\\\x2a\\\x2c\\\x23\\\x21\\\x25\\\x5e\\\x26\\\x2b\\\x3c\\\x3e\\\x2e\\\x27\\\x3f\\\x7c\\\x60]+"
ANYSPACE = "[ ]*"
SINGLESPACE = " "
COLON = ":"
COMMA = ","
ATSIGN = "@"
DOLLARSIGN = "$"
ESCAPED_DOLLARSIGN = "\\$"
PLUSSIGN = "+"
ESCAPED_PLUSSIGN = "\\+"
TILDA = "~"
LBRACKET = "["
RBRACKET = "]"
LCBRACKET = "{"
RCBRACKET = "}"
LPARENT = "("
ESCAPED_LPARENT = "\\("
RPARENT = ")"
ESCAPED_RPARENT = "\\)"
EQSIGN = "="
QUOTE = "\""
NEWLINE = "\n"
WIN_NEWLINE = "\r\n"
NULL = "\x00"
BSLASH = "\\"
FSLASH = "/"

def delete_indices_from_string(thestr, list_indices):

    if thestr is None:
        return None
    if not isinstance(thestr, str):
        return None
    if thestr == "":
        return None

    if list_indices is None:
        return None
    if not isinstance(list_indices, list):
        return None
    if len(list_indices) == 0:
        return None

    for i in list_indices:
        if i >= len(thestr) or i < 0:
            return None

    # credits to https://stackoverflow.com/questions/23308295/remove-multiple-indices-of-a-string
    return "".join([char for idx, char in enumerate(thestr) if idx not in list_indices])

def pop_surrounding_char(thestr, cl, cr):
    # returns tuple: the resulting string, plus a bool indicating
    # whether both were found and removed or not
    pops = 0
    thestr = thestr.strip()
    if len(thestr) > 0:
        if thestr[0] == cl:
            thestr = thestr[1:]
            pops += 1
    if len(thestr) > 0:
        if thestr[len(thestr)-1] == cr:
            thestr = thestr[:len(thestr)-1]
            pops += 1
    res = False
    if pops == 2:
        res = True
    return res, thestr

def guarded_split(source, separator, guard_ch, escape_ch):

    if not isinstance(source, str):
        return None
    if source == "":
        return None
    if not isinstance(separator, str):
        return None
    if len(separator) != 1:
        return None
    if not isinstance(guard_ch, str):
        return None
    if len(guard_ch) != 1:
        return None
    if not isinstance(escape_ch, str):
        return None
    if len(escape_ch) != 1:
        return None
    if guard_ch == escape_ch:
        return None

    source_local = source
    result = []

    while True:

        if len(source_local) == 0:
            return result

        p = guarded_find(source_local, separator, guard_ch, escape_ch)
        if p is None:
            return None
        if p == -1:
            break

        next_piece = source_local[:p]
        source_local = source_local[p + len(separator):]
        if len(next_piece) > 0:
            result.append(next_piece)

    result.append(source_local)
    return result

def guarded_find(source, target, guard_ch, escape_ch):

    if not isinstance(source, str):
        return None
    if source == "":
        return None
    if not isinstance(target, str):
        return None
    if target == "":
        return None
    if not isinstance(guard_ch, str):
        return None
    if len(guard_ch) != 1:
        return None
    if guard_ch in target:
        return None
    if not isinstance(escape_ch, str):
        return None
    if len(escape_ch) != 1:
        return None
    if escape_ch in target:
        return None
    if guard_ch == escape_ch:
        return None

    guarded = False
    target_index = 0
    matching_target = False
    match_begin_index = None
    escaping = False

    for i in range(len(source)):

        if source[i] == guard_ch and not escaping:
            guarded = not guarded
            target_index = 0
            matching_target = False
            match_begin_index = None
            continue

        if guarded:

            if escaping:
                escaping = False
            else:
                if source[i] == escape_ch:
                    escaping = True

        else:

            if matching_target:

                if source[i] == target[target_index]:
                    # keep on matching target
                    target_index += 1
                    if target_index == len(target):
                        # successful target match
                        return match_begin_index

                else:
                    # matching target failed - reset
                    target_index = 0
                    matching_target = False
                    match_begin_index = None

            else:

                if source[i] == target[0]:
                    # start matching target
                    target_index = 1
                    matching_target = True
                    match_begin_index = i
                    if target_index == len(target):
                        # successful target match
                        return match_begin_index

    return -1

def opt_get(thestr, sep_ch):
    if thestr is None:
        return None, None
    if thestr == "":
        return None, None
    if thestr.find(sep_ch) == -1:
        return thestr, ""
    thesplit = thestr.strip().split(sep_ch)
    if len(thesplit) != 2:
        return None, None
    thesplit[0] = thesplit[0].strip()
    psc = pop_surrounding_char(thesplit[1].strip(), "\"", "\"")
    if not psc[0]:
        return thesplit[0], None
    return thesplit[0], psc[1]

def split_either_direction(thestr, term_chars, reverse=False):

    # validate thestr
    if thestr is None:
        return None
    if not isinstance(thestr, str):
        return None
    if len(thestr) == 0:
        return None

    # validate term_chars
    if term_chars is None:
        return None
    if not isinstance(term_chars, list):
        return None
    if len(term_chars) == 0:
        return None

    range_start = None
    range_end = None

    if reverse:
        range_start = len(thestr)-1
        range_end = -1
        fs = -1
    else:
        range_start = 0
        range_end = len(thestr)
        fs = 1

    # get the next
    for i in range(range_start, range_end, fs):
        if thestr[i] in term_chars:
            return (thestr[:i], thestr[i:])

    # no matches
    return None

def split_next(thestr, term_chars):
    return split_either_direction(thestr, term_chars, False)

def split_last(thestr, term_chars):
    return split_either_direction(thestr, term_chars, True)

def remove_of_either_direction(thestr, thechr, reverse=False):

    if thestr is None:
        return False, None
    if thestr == "":
        return False, None
    if not isinstance(thestr, str):
        return False, None

    if thechr is None:
        return False, None
    if thechr == "":
        return False, None
    if not isinstance(thechr, str):
        return False, None

    if reverse:
        n = thestr.rfind(thechr)
    else:
        n = thestr.find(thechr)

    if n == -1:
        return False, thestr

    if not reverse:
        n +=1

    if n == len(thestr):
        return True, ""

    if n > len(thestr):
        return False, ""

    if reverse:
        return True, thestr[:n]
    else:
        return True, thestr[n:]

def remove_next_of(thestr, thechr):
    return remove_of_either_direction(thestr, thechr, False)

def remove_last_of(thestr, thechr):
    return remove_of_either_direction(thestr, thechr, True)

def scan_and_slice(thestr, theregex):

    if thestr is None:
        return None, None
    if not isinstance(thestr, str):
        return None, None

    r = re.search(theregex, thestr)

    if r is None:
        # no match
        return False, thestr
    else:
        span_ret = r.span()
        found_str = r[0]
        sliced_str = thestr[0:span_ret[0]] + thestr[span_ret[1]:]
        return True, (found_str, sliced_str)

def scan_and_slice_beginning(thestr, theregex):
    return scan_and_slice(thestr, "\\A" + theregex)

def scan_and_slice_end(thestr, theregex):
    return scan_and_slice(thestr, theregex + "\\Z")

def next_not_escaped_slice(thestr, sentinel_char, escape_char):

    if thestr is None:
        return False, None
    if not isinstance(thestr, str):
        return False, None
    if thestr == "":
        return False, None

    if sentinel_char is None:
        return False, None
    if not isinstance(sentinel_char, str):
        return False, None
    if sentinel_char == "":
        return False, None

    if escape_char is None:
        return None, None
    if not isinstance(escape_char, str):
        return None, None
    if escape_char == "":
        return False, None

    skip_next = False
    c = -1
    for i in thestr:
        c+=1

        if skip_next:
            skip_next = False
            if i == sentinel_char:
                continue

        if i == escape_char:
            skip_next = True
            continue

        if i == sentinel_char:
            return True, (thestr[:c], thestr[c:])

    return False, None

def last_not_escaped_slice(thestr, sentinel_char, escape_char):

    if thestr is None:
        return False, None
    if not isinstance(thestr, str):
        return False, None
    if thestr == "":
        return False, None

    if sentinel_char is None:
        return False, None
    if not isinstance(sentinel_char, str):
        return False, None
    if sentinel_char == "":
        return False, None

    if escape_char is None:
        return None, None
    if not isinstance(escape_char, str):
        return None, None
    if escape_char == "":
        return False, None

    for i in range(len(thestr)-1, -1, -1):

        if thestr[i] == sentinel_char:

            # checks if this sentinel character ocurrence is escaped. if so, skip it.
            pp = i -1 # previous position
            if pp >= 0:
                if thestr[pp] == escape_char:
                    continue

            return True, (thestr[i+1:], thestr[:i+1])

    return False, None

def slice_left_strip(thestr, find_char):

    if thestr is None:
        return False, None
    if not isinstance(thestr, str):
        return False, None
    if thestr == "":
        return False, None

    if find_char is None:
        return False, None
    if not isinstance(find_char, str):
        return False, None
    if find_char == "":
        return False, None

    n = thestr.find(find_char)
    if n == -1:
        return False, None

    return True, (thestr[0:n]).strip()

def scan_simple(thestr, theregex):

    result = re.match(theregex, thestr)
    if result is None:
        return False
    return len(result[0]) == len(thestr)

def scan_largest_of(target_str, target_str_offset, source_str_list):

    largest_found = 0
    index_largest_found = None
    largest_available = 0
    map_src_offsets = {}

    for i in range(len(source_str_list)):
        e = source_str_list[i]
        if e in map_src_offsets:
            continue
        map_src_offsets[e] = [i, 0]
        if len(e) > largest_available:
            largest_available = len(e)

    scan_count = 0
    for idx in range(target_str_offset, len(target_str)):
        scan_count += 1

        c = target_str[idx]

        no_matches = True
        for e in map_src_offsets:

            if scan_count > len(e):
                continue

            if c == e[map_src_offsets[e][1]]:
                map_src_offsets[e][1] += 1
                no_matches = False
            else:
                map_src_offsets[e][1] = 0

            if map_src_offsets[e][1] == len(e):
                if len(e) > largest_found:
                    largest_found = len(e)
                    index_largest_found = map_src_offsets[e][0]

        if no_matches:
            break

        if largest_found == largest_available:
            break

    return index_largest_found

def descape(thestr, escape_char):

    if thestr is None:
        return False, None
    if not isinstance(thestr, str):
        return False, None
    if thestr == "":
        return True, ""

    if escape_char is None:
        return False, None
    if not isinstance(escape_char, str):
        return False, None
    if escape_char == "":
        return False, None

    list_escape = []

    # first step: detect ocurrences of the escape char
    skip_next = False
    for i in range(len(thestr)):

        if skip_next:
            skip_next = False
            continue

        if thestr[i] == escape_char:
            skip_next = True
            list_escape.append(i)

    if len(list_escape) == 0:
        return True, thestr

    # second step is to just remove the relevant indices
    return True, delete_indices_from_string(thestr, list_escape)

def escape(thestr, escape_char, target_chars):

    if thestr is None:
        return False, None
    if not isinstance(thestr, str):
        return False, None
    if thestr == "":
        return False, None

    if escape_char is None:
        return False, None
    if not isinstance(escape_char, str):
        return False, None
    if escape_char == "":
        return False, None

    if target_chars is None:
        return None, None
    if not isinstance(target_chars, list):
        return None, None
    if len(target_chars) == 0:
        return False, None

    result = ""
    for a in thestr:
        if a in target_chars or a == escape_char:
            result += escape_char
        result += a

    return True, result

if __name__ == "__main__":
    print("Hello from %s" % path_utils.basename_filtered(__file__))
