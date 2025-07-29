#!/usr/bin/env python3

import sys
import os

import path_utils
import detect_repo_type

def filter_extension_is(path, params):
    filename_ext = path_utils.getextension(path)
    return filename_ext in params

def filter_extension_is_not(path, params):
    return not filter_extension_is(path, params)

def filter_has_not_middle_pieces(path, params):
    return not filter_has_middle_pieces(path, params)

def filter_has_middle_pieces(path, params):
    path_pieces = path_utils.splitpath(path, "auto")
    middle_pieces = params

    if (len(path_pieces) < 1) or (len(middle_pieces) < 1):
        return False

    pp = 0
    mp = 0

    while True:

        if middle_pieces[mp] == "*":

            if mp+1 == len(middle_pieces): # last asterisk. match.
                return True

            if middle_pieces[mp+1] == "*": # frivolous/repeated asterisk. ignore and forward.
                mp +=1
                continue

            found_next = False
            for i in range(pp, len(path_pieces)): # find next match.
                if path_pieces[i] == middle_pieces[mp+1]:
                    found_next = True
                    pp = i
                    break

            if not found_next:
                return False

            mp +=1
            if mp == len(middle_pieces):
                return True
            elif pp == len(path_pieces): # last piece but there were still middle pieces to match. no match.
                return False
            else:
                continue

        else: # not asterisk

            if middle_pieces[mp] == path_pieces[pp]:

                mp += 1
                pp += 1

                if mp == len(middle_pieces): # last non asterisk. match.
                    if pp != len(path_pieces): # matched all middle pieces, but the last middle piece is not an asterisk and the are more path pieces. no match.
                        return False
                    return True
                elif pp == len(path_pieces): # last piece ...
                    # are there any other pieces to match other than asterisks?
                    other_than_asterisk = False
                    for c in middle_pieces[mp:]:
                        if c != "*":
                            other_than_asterisk = True
                            break
                    return (not other_than_asterisk) # if last was asterisk, give it a match. otherwise no.
                else:
                    continue # still good. continue.

            else:
                return False # no match

    return False

def filter_has_middle_repos(path, params):

    path_pieces = path_utils.splitpath(path, "auto")
    if (len(path_pieces) < 1):
        return False

    current_path = path_utils.backpedal_path(path)
    while current_path is not None:
        if detect_repo_type.is_any_repo_type(detect_repo_type.detect_repo_type(current_path)[1]):
            return True
        current_path = path_utils.backpedal_path(current_path)

    return False

def filter_has_not_middle_repos(path, params):
    return not filter_has_middle_repos(path, params)

def filter_is_last_not_equal_to(path, params):
    return not filter_is_last_equal_to(path, params)

def filter_is_last_equal_to(path, params):
    if path_utils.basename_filtered(path) == params:
        return True
    return False

def filter_is_not_repo(path, params):
    v = filter_is_repo(path, params)
    if v is None:
        return None
    return not v

def filter_is_repo(path, params):
    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return None
    return detect_repo_type.is_any_repo_type(r)

def filter_path_not_exists(path, params):
    return not filter_path_exists(path, params)

def filter_path_exists(path, params):
    return os.path.exists(path)

def filter_all_positive(path, params):
    return True

def filter_all_negative(path, params):
    return False

def and_adapter(predicate, func, path, params):
    r = func(path, params)
    if predicate is None:
        return r
    r &= predicate
    return r

def or_adapter(predicate, func, path, params):
    r = func(path, params)
    if predicate is None:
        return r
    r |= predicate
    return r

def filter_path_list_and(path_list, filter_functions):
    return filter_path_list(path_list, filter_functions, and_adapter)

def filter_path_list_or(path_list, filter_functions):
    return filter_path_list(path_list, filter_functions, or_adapter)

def filter_path_list(path_list, filter_functions, predicate_adapter):

    if not isinstance(path_list, list):
        return None

    if not isinstance(filter_functions, list):
        return None

    for f in filter_functions:
        if not isinstance(f, tuple):
            return None
        if not len(f) == 2:
            return None

    return_list = []

    for p in path_list:

        all_filters_ok = None
        for f in filter_functions:

            func, params = f
            all_filters_ok = predicate_adapter(all_filters_ok, func, p, params)

        if all_filters_ok:
            return_list.append(p)

    return return_list

def puaq(selfhelp):
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    puaq(False)
