#!/usr/bin/env python3

import sys
import os

import input_checked_passphrase
import check_mounted
import terminal_colors
import backup_engine

class ArtifactBase:
    def __init__(_self, thepath, listexceptions):
        """
        thepath must be a string, and *never* a list
        listexceptions is a list of strings containing exceptions
        """
        _self.thepath = thepath
        _self.listexceptions = listexceptions

    def get_path(_self):
        return _self.thepath
    def get_list_exceptions(_self):
        return _self.listexceptions
    def validate_exceptions(_self):
        for ex_it in _self.listexceptions:
            fp = os.path.join(_self.thepath, ex_it)
            if not os.path.exists(fp):
                return False, ex_it
        return True, ""

def make_backup_artifacts_list(artifacts_base):
    retlist = []
    for cur_base in artifacts_base:
        for cur_dir in os.listdir(cur_base.get_path()):
            if not cur_dir in cur_base.get_list_exceptions():
                retlist.append(os.path.join(cur_base.get_path(), cur_dir))
    return retlist

def read_config(config_file):

    BKPREPARATION = ""
    BKARTIFACTS_BASE = []
    BKARTIFACTS_BASE_EXCEPTION = []
    BKTARGETS_ROOT = []
    BKTEMP = ""
    BKTARGETS_BASEDIR = ""
    BKCHECKMOUNTED = ""

    if not os.path.exists(config_file):
        print("%sConfig file [%s] does not exist.%s" % (terminal_colors.TTY_RED, config_file, terminal_colors.TTY_WHITE))
        return False, ()

    cfg_contents = ""
    with open(config_file) as f:
        cfg_contents = f.read()

    for line in cfg_contents.split("\n"):
        line_t = line.strip()
        if line_t == "":
            continue

        if line_t[0] == "#":
            continue

        # cleanup variables
        var_name, var_value_and_options = line_t.split("=")
        var_name = var_name.strip()
        var_value_and_options = var_value_and_options.strip()

        var_value = ""
        var_options = ""

        try:
            var_value, var_options = var_value_and_options.split(" - ")
        except ValueError:
            var_value = var_value_and_options

        var_value = var_value.strip()
        var_options = var_options.strip()

        if var_name == "":
            print("%sEmpty var name: [%s]%s" % (terminal_colors.TTY_RED, line_t, terminal_colors.TTY_WHITE))
            return False, ()

        if var_value == "":
            print("%sEmpty var value: [%s]%s" % (terminal_colors.TTY_RED, line_t, terminal_colors.TTY_WHITE))
            return False, ()

        # resolve value name (env vars)
        var_value = os.path.expandvars(var_value)
        if "$" in var_value:
            print("%sVariable expansion failed: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
            return False, ()

        # assign values to policy variables
        if var_name == "BKPREPARATION":
            if not os.path.exists(var_value):
                print("%sBKPREPARATION does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
                return False, ()
            BKPREPARATION = var_value

        elif var_name == "BKARTIFACTS_BASE_EXCEPTION":
            # cant be validated now - will be used as filters and be validated later
            BKARTIFACTS_BASE_EXCEPTION.append(var_value)

        elif var_name == "BKARTIFACTS_BASE":
            if not os.path.exists(var_value):
                print("%sBKARTIFACTS_BASE does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
                return False, ()
            new_art_base = ArtifactBase(var_value, BKARTIFACTS_BASE_EXCEPTION)
            r, v = new_art_base.validate_exceptions()
            if not r:
                print("%sBKARTIFACTS_BASE_EXCEPTION does not point to a valid path: [%s]. Parent BKARTIFACTS_BASE is: [%s]%s" % (terminal_colors.TTY_RED, v, var_value, terminal_colors.TTY_WHITE))
                return False, ()
            BKARTIFACTS_BASE.append(new_art_base)
            BKARTIFACTS_BASE_EXCEPTION = []

        elif var_name == "BKTARGETS_ROOT":
            if not os.path.exists(var_value):
                print("%sBKTARGETS_ROOT does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
                return False, ()
            if not "nocheckmount" in var_options:
                if not check_mounted.checkmounted(var_value):
                    print("%sFailed to validate mountpoint of %s. Aborting.%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
                    return False, ()

            BKTARGETS_ROOT.append(var_value)

        elif var_name == "BKTEMP":
            BKTEMP = var_value

        elif var_name == "BKTARGETS_BASEDIR":
            BKTARGETS_BASEDIR = var_value

        else:
            print("%sUnrecognized variable: [%s]%s" % (terminal_colors.TTY_RED, var_name, terminal_colors.TTY_WHITE))
            return False, ()

    ret = True, (BKPREPARATION, BKARTIFACTS_BASE, BKTARGETS_ROOT, BKTARGETS_BASEDIR, BKTEMP)
    return ret

def run_backup(config_file, pass_hash_file):

    # reads config file
    r_cfg, v_cfg = read_config(config_file)
    if not r_cfg:
        print("%sFailed reading config file: [%s]%s" % (terminal_colors.TTY_RED, config_file, terminal_colors.TTY_WHITE))
        return False

    # gets and checks the passphrase
    r_pp, passphrase = input_checked_passphrase.get_checked_passphrase(pass_hash_file)
    if not r_pp:
        print("%sHash doesn't check. Aborting...%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
        return False

    # call the backup engine
    bkeng = backup_engine.BackupEngine(v_cfg[0], make_backup_artifacts_list(v_cfg[1]), v_cfg[2], v_cfg[3], v_cfg[4], passphrase)
    bkeng_ret = bkeng.run()
    return bkeng_ret

def puaq():
    print("Usage: %s config_file pass_hash_file" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    config_file = sys.argv[1]
    pass_hash_file = sys.argv[2]

    run_backup(config_file, pass_hash_file)
