#!/usr/bin/env python3

import sys
import os

import input_checked_passphrase
import check_mounted
import terminal_colors
import fsquery
import path_utils
import dsl_type20

import backup_engine

class ArtifactBase:
    def __init__(_self, thepath, listexceptions, descend):
        """
        thepath must be a string, and *never* a list
        listexceptions is a list of strings containing exceptions
        descend is a boolean determining whether thepath should be "visited" - and as
        a result, every item inside thepath should become a separate artifact
        """
        _self.thepath = thepath
        _self.listexceptions = listexceptions
        _self.descend = descend

    def get_path(_self):
        return _self.thepath
    def get_list_exceptions(_self):
        return _self.listexceptions
    def get_descend(_self):
        return _self.descend
    def validate_exceptions(_self):
        for ex_it in _self.listexceptions:
            fp = path_utils.concat_path(_self.thepath, ex_it)
            if not os.path.exists(fp):
                return False, ex_it
        return True, ""

def make_backup_artifacts_list(artifacts_base):
    retlist = []
    for cur_base in artifacts_base:
        if not cur_base.get_descend():
            retlist.append(cur_base.get_path())
        else:
            for cur_dir in fsquery.makecontentlist(cur_base.get_path(), False, True, True, True, True, True, None):
                add_cur = True
                for cur_ex in cur_base.get_list_exceptions():
                    if cur_dir == path_utils.concat_path(cur_base.get_path(), cur_ex):
                        add_cur = False
                        break
                if add_cur:
                    retlist.append(path_utils.concat_path(cur_base.get_path(), os.path.basename(cur_dir)))
    return retlist

def read_config(config_file):

    # read the cfg file and setup the dsl parser
    if not os.path.exists(config_file):
        print("%sConfig file [%s] does not exist.%s" % (terminal_colors.TTY_RED, config_file, terminal_colors.TTY_WHITE))
        return False, ()

    cfg_contents = ""
    with open(config_file) as f:
        cfg_contents = f.read()

    dsl = dsl_type20.DSLType20(True, True)
    v, r = dsl.parse(cfg_contents)
    if not v:
        print("%sFailed parsing [%s]: %s%s" % (terminal_colors.TTY_RED, config_file, r, terminal_colors.TTY_WHITE))
        return False, ()

    # define toplevel vars
    BKPREPARATION = ""
    BKPREPARATION_PARAMS = []
    BKSOURCE = []
    BKTARGETS_ROOT = []
    BKTEMP = ""
    BKTARGETS_BASEDIR = ""

    vars = dsl.getallvars()
    for v in vars:

        var_name = v[0]
        var_value = v[1]
        var_options = v[2]

        # assign values to policy variables
        if var_name == "BKPREPARATION":
            if not os.path.exists(var_value):
                print("%sBKPREPARATION does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
                return False, ()
            BKPREPARATION = var_value
            for o in var_options:
                if o[0] == "param":
                    BKPREPARATION_PARAMS.append(o[1])

        elif var_name == "BKSOURCE":
            if not os.path.exists(var_value):
                print("%sBKSOURCE does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
                return False, ()

            BKSOURCE_EXCEPTIONS = []
            descend = False
            for o in var_options:
                if o[0] == "ex":
                    BKSOURCE_EXCEPTIONS.append(o[1])
                elif o[0] == "descend":
                    descend = True

            new_art_base = ArtifactBase(var_value, BKSOURCE_EXCEPTIONS, descend)
            r, v = new_art_base.validate_exceptions()
            if not r:
                print("%sBKSOURCE_EXCEPTIONS does not point to a valid path: [%s]. BKSOURCE is: [%s]%s" % (terminal_colors.TTY_RED, v, var_value, terminal_colors.TTY_WHITE))
                return False, ()
            BKSOURCE.append(new_art_base)

        elif var_name == "BKTARGETS_ROOT":
            if not os.path.exists(var_value):
                print("%sBKTARGETS_ROOT does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.TTY_WHITE))
                return False, ()
            if not dsl_type20.hasopt_var(v, "nocheckmount"):
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

    if len(BKSOURCE) == 0:
        print("%sBKSOURCE can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
        return False, ()
    if len(BKTARGETS_ROOT) == 0:
        print("%sBKTARGETS_ROOT can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
        return False, ()
    if len(BKTEMP) == 0:
        print("%sBKTEMP can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
        return False, ()
    if len(BKTARGETS_BASEDIR) == 0:
        print("%sBKTARGETS_BASEDIR can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
        return False, ()

    ret = True, ( (BKPREPARATION, BKPREPARATION_PARAMS), BKSOURCE, BKTARGETS_ROOT, BKTARGETS_BASEDIR, BKTEMP)
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
