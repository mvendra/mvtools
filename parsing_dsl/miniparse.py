#!/usr/bin/env python3

import sys
import os

import re

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

def guarded_split(thestr, sep_ch, guard_chs):
    """
    guarded_split allows you to split a string by sep_ch, while
    preserving contents that come inside of guard_chs (a list of tuples that specify
    a beginning guard char and an ending guard char)
    for example, guarded_split("variable = |val=ue|", "=", [("|", "|")]) would
    return ["variable ", " |val=ue|"]
    """

    if thestr == "":
        return []
    if not isinstance(thestr, str):
        return None
    if not isinstance(guard_chs, list):
        return None
    for t in guard_chs:
        if not isinstance(t, tuple):
            return None
        if len(t) != 2:
            return None

    ret = []
    flag_guard_on = False
    last_piece_beg = 0
    ecg = None # expected closing guard
    for i in range(len(thestr)):

        if i == len(thestr) - 1:
            ret.append(thestr[last_piece_beg:])

        c = thestr[i]

        if flag_guard_on:
            if c == ecg:
                flag_guard_on = False
                ecg = None
                continue
        else:
            for g in guard_chs:
                if c == g[0]:
                    ecg = g[1]
                    flag_guard_on = True
                    continue

        if c == sep_ch:
            if flag_guard_on or not i > last_piece_beg:
                continue

            ret.append(thestr[last_piece_beg:i])
            last_piece_beg = i+1

    return ret

def guarded_right_cut(thestr, sep_seq, guard_ch):

    if not isinstance(thestr, str):
        return None
    if thestr == "":
        return None
    if not isinstance(sep_seq, list):
        return None
    if len(sep_seq) < 1:
        return None
    if not isinstance(guard_ch, str):
        return None
    if guard_ch == "":
        return None
    if sep_seq[0] == guard_ch:
        return None

    guarded = False
    matching = False
    sepseq_index = 0
    match_begin_index = None

    for i in range(len(thestr)):

        if matching:

            if thestr[i] == sep_seq[sepseq_index]:
                # keep on matching
                sepseq_index += 1
                if sepseq_index == len(sep_seq):
                    # successful match.
                    matching = False
                    sepseq_index = 0
                    if not guarded:
                        return thestr[:match_begin_index]

            else:
                # matching failed. reset
                sepseq_index = 0
                matching = False
                match_begin_index = None

        else:

            if thestr[i] == sep_seq[0]:
                # start matching
                matching = True
                sepseq_index = 1
                match_begin_index = i
                if sepseq_index == len(sep_seq):
                    # successful match.
                    matching = False
                    sepseq_index = 0
                    if not guarded:
                        return thestr[:match_begin_index]

        if thestr[i] == guard_ch:
            guarded = not guarded

    return thestr

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
    print("Hello from %s" % os.path.basename(__file__))
