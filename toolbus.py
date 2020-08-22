#!/usr/bin/env python3

import sys
import os

import path_utils
import dsl_type20

DB_EXTENSION = "txt"
INTERNAL_DB_FILENAME = "toolbus_internal"
TOOLBUS_ENVVAR = "MVTOOLS_TOOLBUS_BASE"

def bootstrap_internal_toolbus_db(_filename):

    if os.path.exists(_filename):
        return False

    contents = "" # mvtodo

    with open(_filename, "w") as f:
        f.write(contents)

    return True

def get_db_handle(_db_name, bootstrap_internal=False):

    if _db_name is None:
        return False, "Invalid parameters."

    try:
        db_base = os.environ[TOOLBUS_ENVVAR]
    except:
        return False, "Failed setting up toolbus. Is the %s environment variable defined?" % TOOLBUS_ENVVAR

    if not os.path.exists(db_base):
        return False, "Failed setting up toolbus - base path [%s] does not exist." % db_base

    db_file_full = path_utils.concat_path(db_base, _db_name)

    if not os.path.exists(db_file_full):
        if bootstrap_internal:
            if not bootstrap_internal_toolbus_db(db_file_full):
                return False, "Failed setting up toolbus - unable to bootstrap toolbus internal database."
        else:
            return False, "Failed setting up toolbus - database [%s] does not exist." % db_file_full

    db_handle = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(False, False, False))

    db_contents = ""
    with open(db_file_full) as f:
        db_contents = f.read()

    v, r = db_handle.parse(db_contents)
    if not v:
        return False, "Failed setting up toolbus - failed parsing database: %s" % r

    return True, db_handle

def get_handle_internal_db():
    return get_db_handle("%s.%s" % (INTERNAL_DB_FILENAME, DB_EXTENSION), True)

def get_handle_custom_db(_db_name):
    if _db_name == INTERNAL_DB_FILENAME:
        return False, "Failed setting up toolbus - the database name [%s] is reserved." % INTERNAL_DB_FILENAME
    return get_db_handle("%s.%s" % (_db_name, DB_EXTENSION))

def get_signal(_sig_name):

    # mvtodo

    v, r = get_handle_internal_db()
    if not v:
        return False, r

    signal_value = (r.get_vars(_sig_name))

    return True, signal_value

def set_signal(_sig_name, _sig_val):
    pass # mvtodo

def get_field(_db_name, _context, _var):

    v, r = get_handle_custom_db(_db_name)
    if not v:
        return False, r

    vars = r.get_vars(_var, _context)
    if vars is None:
        return False, "Variable [%s] is not present (database: [%s], context: [%s])" % (_var, _db_name, _context)

    if len(vars) != 1:
        return False, "Variable [%s] is not present (database: [%s], context: [%s])" % (_var, _db_name, _context)

    return True, vars[0]

def set_field(_db_name, _context, _var):
    pass # mvtodo

if __name__ == "__main__":
    print("Hello from toolbus.")
