#!/usr/bin/env python3

import sys
import os

import path_utils
import mvtools_exception
import toolbus

import getfromclipboard
import sendtoclipboard

CLIPSTACK_TOOLBUS_DATABASE = "mvtools_clipstack"
CLIPSTACK_TOOLBUS_CONTEXT = "clipboard_stack"
CLIPSTACK_TOOLBUS_HEADER = "header_count"

def _ensure_toolbus_db():

    v, r = toolbus.get_all_fields(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT)
    if v and r is not None:
        return

    first_error = None
    v, r = toolbus.bootstrap_custom_toolbus_db(CLIPSTACK_TOOLBUS_DATABASE)
    if not v:
        first_error = r # save it - this might be recoverable (if the db file is simply empty)

    v, r = toolbus.set_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, CLIPSTACK_TOOLBUS_HEADER, "0", [])
    if not v:
        errmsg = ""
        if first_error is None:
            errmsg = r
        else:
            errmsg = "First error: [%s]. Second error: [%s]" % (first_error, r)
        raise mvtools_exception.mvtools_exception(errmsg)

def clipstack_push():

    _ensure_toolbus_db()

    v, r = toolbus.get_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, CLIPSTACK_TOOLBUS_HEADER)
    if not v:
        return False, r
    field_header_count = r

    v, r = toolbus.get_all_fields(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT)
    if not v:
        return False, r
    all_entries = r

    # check for db tampering
    if (int(field_header_count[1]) + 1) != len(all_entries):
        return False, "Database is corrupted (nonmatching header-count vs number of actual entries)"

    # store the current clipboard contents
    clipboard_readout = getfromclipboard.getfromclipboard()
    if clipboard_readout is None:
        raise mvtools_exception.mvtools_exception("clipstack_push: call to getfromclipboard failed.")
    v, r = toolbus.set_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, str(int(field_header_count[1]) + 1), clipboard_readout, [])
    if not v:
        return False, r

    # update the header count
    v, r = toolbus.set_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, CLIPSTACK_TOOLBUS_HEADER, str(int(field_header_count[1]) + 1), [])
    if not v:
        return False, r

    return True, None

def clipstack_top():

    v, r = clipstack_top_delegate()
    if not v:
        return False, r
    return True, r[0]

def clipstack_top_delegate():

    _ensure_toolbus_db()

    v, r = toolbus.get_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, CLIPSTACK_TOOLBUS_HEADER)
    if not v:
        return False, r
    field_header_count = r

    v, r = toolbus.get_all_fields(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT)
    if not v:
        return False, r
    all_entries = r

    # check for db tampering
    if (int(field_header_count[1]) + 1) != len(all_entries):
        return False, "Database is corrupted (nonmatching header-count vs number of actual entries)"

    # retrieve the header count
    v, r = toolbus.get_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, CLIPSTACK_TOOLBUS_HEADER)
    if not v:
        return False, r
    header_count = r
    header_count = int(header_count[1])

    if header_count == 0:
        return False, "Clipboard stack is empty"

    # retrieve the last saved clipboard contents
    v, r = toolbus.get_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, str(header_count))
    if not v:
        return False, r
    last_saved = r

    if last_saved is None:
        return False, "Position [%s] is unexpectedly empty!" % header_count

    return True, (last_saved[1], header_count)

def clipstack_pop():

    v, r = clipstack_top_delegate()
    if not v:
        return False, r
    last_saved = r[0]
    header_count = r[1]

    # update the clipboard
    if not sendtoclipboard.sendtoclipboard(last_saved):
        raise mvtools_exception.mvtools_exception("clipstack_pop: call to sendtoclipboard failed.")

    # remove the last field (top-of-stack)
    v, r = toolbus.remove_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, str(header_count))
    if not v:
        return False, r

    # update the header count
    v, r = toolbus.set_field(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT, CLIPSTACK_TOOLBUS_HEADER, str(header_count-1), [])
    if not v:
        return False, r

    return True, None

def clipstack_clear():

    _ensure_toolbus_db()

    v, r = toolbus.remove_table(CLIPSTACK_TOOLBUS_DATABASE, CLIPSTACK_TOOLBUS_CONTEXT)
    if not v:
        return False, r

    _ensure_toolbus_db()

    return True, None

def _info_helper(entries_count):
    if entries_count == 1:
        return "entry"
    return "entries"

def clipstack_info():

    v, r = clipstack_top_delegate()
    if not v:
        return False, r
    return True, "Clipboard stack has [%s] %s" % (r[1], _info_helper(r[1]))

def clipstack(operation):

    if operation == "push":
        return clipstack_push()
    elif operation == "pop":
        return clipstack_pop()
    elif operation == "top":
        return clipstack_top()
    elif operation == "clear":
        return clipstack_clear()
    elif operation == "info":
        return clipstack_info()
    else:
        return False, "Unknown operation: [%s]" % operation

    return False, "clipstack not_reached"

def puaq():
    print("Usage: %s [push | pop | top | clear | info]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    operation = sys.argv[1]
    v, r = clipstack(operation)
    if r is not None:
        print(r)
    if not v:
        sys.exit(1)
