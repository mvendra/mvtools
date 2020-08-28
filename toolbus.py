#!/usr/bin/env python3

import sys
import os

import path_utils
import dsl_type20

import trylock

TOOLBUS_ENVVAR = "MVTOOLS_TOOLBUS_BASE"
DB_EXTENSION = "txt"
INTERNAL_DB_FILENAME = "toolbus_internal"
TOOLBUS_SIGNAL_CONTEXT = "toolbus_internal_signals_context"

def bootstrap_internal_toolbus_db(_filename):

    if os.path.exists(_filename):
        return False

    db_handle = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(False, False, False))
    db_handle.add_context(TOOLBUS_SIGNAL_CONTEXT)
    bootstrap_contents = db_handle.produce()

    with open(_filename, "a") as f:

        # tries to acquire a mutex lock on this file to prevent concurrent writes
        if not trylock.try_lock_file(f):
            return False, "Unable to acquire write lock on file [%s] (database: [%s], context: [%s])" % (_filename, INTERNAL_DB_FILENAME, TOOLBUS_SIGNAL_CONTEXT)

        f.truncate(0) # clear old contents prior to updating
        f.write(bootstrap_contents)
        f.flush()
        trylock.try_unlock_file(f)

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

def _get_internal(_dh_handle, _db_name, _context, _var):

    vars = _dh_handle.get_vars(_var, _context)
    if vars is None:
        return False, "Variable [%s] is not present (database: [%s], context: [%s])" % (_var, _db_name, _context)

    if len(vars) != 1:
        return False, "Variable [%s] is not present (database: [%s], context: [%s])" % (_var, _db_name, _context)

    return True, vars[0]

def get_signal(_sig_name):

    v, r, ext = get_handle_internal_db()
    if not v:
        return False, r

    v, r = _get_internal(r, "(internal toolbus database)", TOOLBUS_SIGNAL_CONTEXT, _sig_name)
    if not v:
        return False, r
    return True, r[1]

def get_field(_db_name, _context, _var):

    v, r, ext = get_handle_custom_db(_db_name)
    if not v:
        return False, r

    return _get_internal(r, _db_name, _context, _var)

def _set_internal(_dh_handle, _db_name, _db_full_file, _context, _var, _val, _opts):

    vars = _dh_handle.get_vars(_var, _context)
    if vars is not None:
        if len(vars) != 0:
            # var already exists. must be removed first so it can then be recreated with new value.
            if not _dh_handle.rem_var(_var, None, _context):
                return False, "Unable to remove variable [%s] (database: [%s], context: [%s])" % (_var, _db_name, _context)

    # add/set new variable
    if not _dh_handle.add_var(_var, _val, _opts, _context):
        return False, "Unable to add variable [%s] (database: [%s], context: [%s])" % (_var, _db_name, _context)

    # serialize updated database
    new_contents = _dh_handle.produce()

    # save changes to file
    with open(_db_full_file, "a") as f:

        # tries to acquire a mutex lock on this file to prevent concurrent writes
        if not trylock.try_lock_file(f):
            return False, "Unable to acquire write lock on file [%s] (database: [%s], context: [%s])" % (_db_full_file, _db_name, _context)

        f.truncate(0) # clear old contents prior to updating
        f.write(new_contents)
        f.flush()
        trylock.try_unlock_file(f)

    return True, None

def set_signal(_sig_name, _sig_val):

    v, r, ext = get_handle_internal_db()
    if not v:
        return False, r

    return _set_internal(r, "(internal toolbus database)", ext, TOOLBUS_SIGNAL_CONTEXT, _sig_name, _sig_val, [])

def set_field(_db_name, _context, _var, _val, _opts):

    v, r, ext = get_handle_custom_db(_db_name)
    if not v:
        return False, r

    return _set_internal(r, _db_name, ext, _context, _var, _val, _opts)

if __name__ == "__main__":
    print("Hello from toolbus.")
