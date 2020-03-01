#!/usr/bin/env python3

import sys
import os

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

def opt_get(thestr, sep_ch):
    if thestr is None:
        return "",""
    if thestr == "":
        return "",""
    if thestr.find(sep_ch) == -1:
        return thestr, ""
    thesplit = thestr.strip().split(sep_ch)
    if len(thesplit) != 2:
        return "",""
    thesplit[0] = thesplit[0].strip()
    thesplit[1] = (pop_surrounding_char(thesplit[1].strip(), "\"", "\""))[1]
    return thesplit[0], thesplit[1]

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
