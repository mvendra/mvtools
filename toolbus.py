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

def get_signal(_sig_name, probe_only=False):

    v, r, ext = get_handle_internal_db()
    if not v:
        return False, r
    _db_handle = r

    v, r = _get_internal(_db_handle, "(internal toolbus database)", TOOLBUS_SIGNAL_CONTEXT, _sig_name)
    if not v:
        return False, r

    if not probe_only: # signal consumed

        # delete the consumed variable
        if not _db_handle.rem_var(_sig_name, None, TOOLBUS_SIGNAL_CONTEXT):
            return False, "Unable to remove variable (already used signal) [%s] (database: [%s], context: [%s])" % (_sig_name, "(internal toolbus database)", TOOLBUS_SIGNAL_CONTEXT)

        new_contents = _db_handle.produce()

        # save changes to file
        with open(ext, "a") as f:

            # tries to acquire a mutex lock on this file to prevent concurrent writes
            if not trylock.try_lock_file(f):
                return False, "Unable to acquire write lock on file [%s] (database: [%s], context: [%s])" % (ext, "(internal toolbus database)", TOOLBUS_SIGNAL_CONTEXT)

            f.truncate(0) # clear old contents prior to updating
            f.write(new_contents)
            f.flush()
            trylock.try_unlock_file(f)

    return True, r[1]

def get_field(_db_name, _context, _var):

    v, r, ext = get_handle_custom_db(_db_name)
    if not v:
        return False, r

    return _get_internal(r, _db_name, _context, _var)

def _set_internal(_dh_handle, _db_name, _db_full_file, _context, _var, _val, _opts, allow_overwrite):

    vars = _dh_handle.get_vars(_var, _context)
    if vars is not None:
        if len(vars) != 0:

            if not allow_overwrite:
                return False, "Setting variable [%s] failed - overwrites are not allowed (database: [%s], context: [%s])" % (_var, _db_name, _context)

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

    return _set_internal(r, "(internal toolbus database)", ext, TOOLBUS_SIGNAL_CONTEXT, _sig_name, _sig_val, [], False)

def set_field(_db_name, _context, _var, _val, _opts):

    v, r, ext = get_handle_custom_db(_db_name)
    if not v:
        return False, r

    return _set_internal(r, _db_name, ext, _context, _var, _val, _opts, True)

def puaq():
    print("Usage: %s [--get-signal signame] [--set-signal signame sigvalue]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    params = sys.argv[1:]
    get_signal_signame_next = False
    set_signal_signame_next = False
    set_signal_sigval_next = False

    get_signame = None
    set_signame = None
    set_sigval = None

    for p in params:

        if get_signal_signame_next:
            get_signal_signame_next = False
            get_signame = p
            continue

        if set_signal_signame_next:
            set_signal_signame_next = False
            set_signal_sigval_next = True
            set_signame = p
            continue

        if set_signal_sigval_next:
            set_signal_sigval_next = False
            set_sigval = p
            continue

        if p == "--get-signal":
            get_signal_signame_next = True
        elif p == "--set-signal":
            set_signal_signame_next = True

    if not get_signame is None:
        v, r = get_signal(get_signame)
        if v:
            print(r)
        else:
            print("Toolbus get_signal failed: %s" % r)
            sys.exit(1)

    if not set_signame is None:
        if set_sigval is None:
            print("--set-signal was specified. It requires two parameters but only one was provided. Aborting.")
            sys.exit(1)
        v, r = set_signal(set_signame, set_sigval)
        if v:
            print("Signal [%s] set." % set_signame)
        else:
            print("Toolbus set_signal failed: %s" % r)
            sys.exit(1)
