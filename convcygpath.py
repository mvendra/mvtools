#!/usr/bin/env python3

import sys
import os

import fsquery
import path_utils
import sendtoclipboard

def puaq():
    print("Usage: %s path" % os.path.basename(__file__))
    sys.exit(1)

def find_drive_letter(target_path):
    pos = target_path.find(":")
    if pos == -1:
        return None
    else:
        dl_path = path_utils.concat_path("/cygdrive", target_path[0:pos].lower())
        return dl_path

def cut_drive_letter(target_path):
    pos = target_path.find(":")
    if pos == -1:
        return None
    else:
        cut_path = target_path[pos+1:]
        return cut_path

def _has_key(map, item):

    try:
        if map[item] == True:
            return True
        else:
            return False
    except:
        return False

def linear_search(item, domain):

    amt = 0
    while (True):
        amt += 1
        if amt >= len(item):
            return None
        if _has_key(domain, item[0:amt]):
            return item[0:amt]

def _ar_to_map(in_ar):
    map = {}
    for it in in_ar:
        map[path_utils.basename_filtered(it)] = True
    return map

def find_next_path(root, path_string):

    if not os.path.exists(root):
        return False, None

    contents = fsquery.makecontentlist(root, False, True, True, True, True, True, [])
    contents_map = _ar_to_map(contents)
    sr = linear_search(path_string, contents_map)
    if sr is None:
        return False, path_string
    else:
        return True, sr

def convert_win_path_to_cygwin_path(target_path):

    final_path = find_drive_letter(target_path)
    if final_path is None:
        final_path = os.getcwd()
    else:
        target_path = cut_drive_letter(target_path)
    if target_path is None:
        return None

    while (True):
        result, next = find_next_path(final_path, target_path)
        target_path = target_path[len(next):]
        final_path = path_utils.concat_path(final_path, next)
        if not result:
            break

    return final_path

def merge_spaces(input):
    ret = ""
    for i in input:
        ret += i + " "
    return ret[0:len(ret)-1]

def escape_spaces(input):
    return input.replace(" ", "\\ ")

if __name__ == "__main__":

    target_path = ""
    if len(sys.argv) < 2:
        puaq()
    target_path = merge_spaces(sys.argv[1:])

    new_path = convert_win_path_to_cygwin_path(target_path)
    new_path = escape_spaces(new_path)
    if new_path is not None:
        sendtoclipboard.sendtoclipboard(new_path)
