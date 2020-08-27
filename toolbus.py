#!/usr/bin/env python3

import sys
import os

import path_utils
import dsl_type20

import trylock
import retry

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
        return False, "Invalid parameters.", None

    try:
        db_base = os.environ[TOOLBUS_ENVVAR]
    except:
        return False, "Failed setting up toolbus. Is the %s environment variable defined?" % TOOLBUS_ENVVAR, None

    if not os.path.exists(db_base):
        return False, "Failed setting up toolbus - base path [%s] does not exist." % db_base, None

    db_file_full = path_utils.concat_path(db_base, _db_name)

    if not os.path.exists(db_file_full):
        if bootstrap_internal:
            if not bootstrap_internal_toolbus_db(db_file_full):
                return False, "Failed setting up toolbus - unable to bootstrap toolbus internal database.", None
        else:
            return False, "Failed setting up toolbus - database [%s] does not exist." % db_file_full, None

    db_handle = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(False, False, False))

    db_contents = ""
    with open(db_file_full) as f:
        db_contents = f.read()

    v, r = db_handle.parse(db_contents)
    if not v:
        return False, "Failed setting up toolbus - failed parsing database: %s" % r, None

    return True, db_handle, db_file_full

def get_handle_internal_db():
    return get_db_handle("%s.%s" % (INTERNAL_DB_FILENAME, DB_EXTENSION), True)

def get_handle_custom_db(_db_name):
    if _db_name == INTERNAL_DB_FILENAME:
        return False, "Failed setting up toolbus - the database name [%s] is reserved." % INTERNAL_DB_FILENAME, None
    return get_db_handle("%s.%s" % (_db_name, DB_EXTENSION))

def get_signal(_sig_name):

    # mvtodo

    v, r, ext = get_handle_internal_db()
    if not v:
        return False, r

    signal_value = (r.get_vars(_sig_name))

    return True, signal_value

def set_signal(_sig_name, _sig_val):

    # mvtodo: retry upon lock failure

    pass # mvtodo

def get_field(_db_name, _context, _var):

    v, r, ext = get_handle_custom_db(_db_name)
    if not v:
        return False, r

    vars = r.get_vars(_var, _context)
    if vars is None:
        return False, "Variable [%s] is not present (database: [%s], context: [%s])" % (_var, _db_name, _context)

    if len(vars) != 1:
        return False, "Variable [%s] is not present (database: [%s], context: [%s])" % (_var, _db_name, _context)

    return True, vars[0]

def set_field(_db_name, _context, _var, _val, _opts):

    v, r, ext = get_handle_custom_db(_db_name)
    if not v:
        return False, r

    vars = r.get_vars(_var, _context)
    if vars is not None:
        if len(vars) != 0:
            # var already exists. must be removed first so it can then be recreated with new value.
            if not r.rem_var(_var, None, _context):
                return False, "Unable to remove variable [%s] (database: [%s], context: [%s])" % (_var, _db_name, _context)

    # add/set new variable
    if not r.add_var(_var, _val, _opts, _context):
        return False, "Unable to add variable [%s] (database: [%s], context: [%s])" % (_var, _db_name, _context)

    # serialize updated database
    new_contents = r.produce()

    # save changes to file
    with open(ext, "a") as f:

        # tries (and retries if needed) to acquire a mutex lock on this file to prevent concurrent writes
        if not retry.retry({}, trylock.try_lock_file, f):
            return False, "Unable to acquire write lock on file [%s] - failed all retries (database: [%s], context: [%s])" % (ext, _db_name, _context)

        f.truncate(0) # clear old contents prior to updating
        f.write(new_contents)
        f.flush()
        trylock.try_unlock_file(f)

    return True, None

if __name__ == "__main__":
    print("Hello from toolbus.")
