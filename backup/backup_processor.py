#!/usr/bin/env python3

import sys
import os

import input_checked_passphrase
import check_mounted
import terminal_colors
import fsquery
import mvtools_exception
import path_utils
import dsl_type20
import convert_unit

import backup_engine

class ArtifactBase:
    def __init__(_self, thepath, listexceptions, descend, abort, warn_size, warn_abort):
        """
        thepath must be a string, and *never* a list
        listexceptions is a list of strings containing exceptions
        descend is a boolean determining whether thepath should be "visited" - and as
        a result, every item inside thepath should become a separate artifact
        abort is a boolean that when True will cause the backup to be cancelled
        if this artifact source is nonexistent. when False, it will be verbosedly skipped.
        warn_size is a size in bytes that, if this artifact source exceeds it, either
        a warning is issued or the backup is cancelled.
        warn_abort is a boolean that determines whether the backup should be cancelled or
        not when warn_size is exceeded
        """
        _self.thepath = thepath
        _self.listexceptions = listexceptions
        _self.descend = descend
        _self.abort = abort
        _self.warn_size = warn_size
        _self.warn_abort = warn_abort
    def get_path(_self):
        return _self.thepath
    def get_list_exceptions(_self):
        return _self.listexceptions
    def get_descend(_self):
        return _self.descend
    def get_abort(_self):
        return _self.abort
    def get_warn_size(_self):
        return _self.warn_size
    def get_warn_abort(_self):
        return _self.warn_abort
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
            retlist.append( ( cur_base.get_path(), cur_base.get_abort(), cur_base.get_warn_size(), cur_base.get_warn_abort() ) )
        else:
            v, r = fsquery.makecontentlist(cur_base.get_path(), False, False, True, True, True, True, True, None)
            if not v:
                raise mvtools_exception.mvtools_exception(r)
            all_detected_dirs = r
            for cur_dir in all_detected_dirs:
                add_cur = True
                for cur_ex in cur_base.get_list_exceptions():
                    if cur_dir == path_utils.concat_path(cur_base.get_path(), cur_ex):
                        add_cur = False
                        break
                if add_cur:
                    retlist.append( ( path_utils.concat_path(cur_base.get_path(), path_utils.basename_filtered(cur_dir)), cur_base.get_abort(), cur_base.get_warn_size(), cur_base.get_warn_abort() ) )
    return retlist

def read_config(config_file):

    # read the cfg file and setup the dsl parser
    if not os.path.exists(config_file):
        print("%sConfig file [%s] does not exist.%s" % (terminal_colors.TTY_RED, config_file, terminal_colors.get_standard_color()))
        return False, ()

    cfg_contents = ""
    with open(config_file) as f:
        cfg_contents = f.read()

    dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(True, True))
    v, r = dsl.parse(cfg_contents)
    if not v:
        print("%sFailed parsing [%s]: %s%s" % (terminal_colors.TTY_RED, config_file, r, terminal_colors.get_standard_color()))
        return False, ()

    # define toplevel vars
    BKPREPARATION = ""
    BKPREPARATION_PARAMS = []
    BKSOURCE = []
    BKTARGETS_ROOT = []
    BKTEMP = ""
    BKTARGETS_BASEDIR = ""
    BKWARNING_EACH = (None, None)
    BKWARNING_FINAL = (None, None)

    v, r = dsl.get_all_variables()
    if not v:
        print("%sFailed fetching variables from config file [%s]: %s%s" % (terminal_colors.TTY_RED, config_file, r, terminal_colors.get_standard_color()))
        return False, ()
    vars = dsl_type20.convert_var_obj_list_to_neutral_format(r)
    for v in vars:

        var_name = v[0]
        var_value = v[1]
        var_options = v[2]

        # assign values to policy variables
        if var_name == "BKPREPARATION":
            if not os.path.exists(var_value):
                print("%sBKPREPARATION does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.get_standard_color()))
                return False, ()
            BKPREPARATION = var_value
            for o in var_options:
                if o[0] == "param":
                    if isinstance(o[1], list):
                        BKPREPARATION_PARAMS += o[1]
                    else:
                        BKPREPARATION_PARAMS.append(o[1])

        elif var_name == "BKSOURCE":
            BKSOURCE_EXCEPTIONS = []
            descend = False
            abort = False
            warn_size = None
            warn_abort = None
            for o in var_options:
                if o[0] == "ex":
                    if isinstance(o[1], list):
                        BKSOURCE_EXCEPTIONS += o[1]
                    else:
                        BKSOURCE_EXCEPTIONS.append(o[1])
                elif o[0] == "descend":
                    descend = True
                elif o[0] == "abort":
                    abort = True
                elif o[0] == "warn_size":
                    bv, sr = convert_unit.convert_to_bytes(o[1])
                    if not bv:
                        print("%sBKSOURCE's warn_size option is malformed: [%s]%s" % (terminal_colors.TTY_RED, o[1], terminal_colors.get_standard_color()))
                        return False, ()
                    warn_size = sr
                elif o[0] == "warn_abort":
                    warn_abort = True

            new_art_base = ArtifactBase(var_value, BKSOURCE_EXCEPTIONS, descend, abort, warn_size, warn_abort)
            r, v = new_art_base.validate_exceptions()
            if not r:
                print("%sBKSOURCE_EXCEPTIONS does not point to a valid path: [%s]. BKSOURCE is: [%s]%s" % (terminal_colors.TTY_RED, v, var_value, terminal_colors.get_standard_color()))
                return False, ()
            BKSOURCE.append(new_art_base)

        elif var_name == "BKTARGETS_ROOT":
            if not os.path.exists(var_value):
                print("%sBKTARGETS_ROOT does not point to a valid path: [%s]%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.get_standard_color()))
                return False, ()
            if not dsl_type20.hasopt_var(v, "nocheckmount"):
                if not check_mounted.checkmounted(var_value):
                    print("%sFailed to validate mountpoint of %s. Aborting.%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.get_standard_color()))
                    return False, ()

            BKTARGETS_ROOT.append(var_value)

        elif var_name == "BKTEMP":
            BKTEMP = var_value

        elif var_name == "BKTARGETS_BASEDIR":
            BKTARGETS_BASEDIR = var_value

        elif var_name == "BKWARNING_EACH":
            bv, sr = convert_unit.convert_to_bytes(var_value)
            if not bv:
                print("%sFailed to convert %s. Aborting.%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.get_standard_color()))
                return False, ()
            conv_value = sr
            warn_each_abort = dsl_type20.hasopt_var(v, "abort")
            BKWARNING_EACH = (conv_value, warn_each_abort)

        elif var_name == "BKWARNING_FINAL":
            bv, sr = convert_unit.convert_to_bytes(var_value)
            if not bv:
                print("%sFailed to convert %s. Aborting.%s" % (terminal_colors.TTY_RED, var_value, terminal_colors.get_standard_color()))
                return False, ()
            conv_value = sr
            warn_each_abort = dsl_type20.hasopt_var(v, "abort")
            BKWARNING_FINAL = (conv_value, warn_each_abort)

        else:
            print("%sUnrecognized variable: [%s]%s" % (terminal_colors.TTY_RED, var_name, terminal_colors.get_standard_color()))
            return False, ()

    if len(BKSOURCE) == 0:
        print("%sBKSOURCE can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.get_standard_color()))
        return False, ()
    if len(BKTARGETS_ROOT) == 0:
        print("%sBKTARGETS_ROOT can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.get_standard_color()))
        return False, ()
    if len(BKTEMP) == 0:
        print("%sBKTEMP can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.get_standard_color()))
        return False, ()
    if len(BKTARGETS_BASEDIR) == 0:
        print("%sBKTARGETS_BASEDIR can't be empty.%s" % (terminal_colors.TTY_RED, terminal_colors.get_standard_color()))
        return False, ()

    ret = True, ( (BKPREPARATION, BKPREPARATION_PARAMS), BKSOURCE, BKTARGETS_ROOT, BKTARGETS_BASEDIR, BKTEMP, (BKWARNING_EACH, BKWARNING_FINAL) )
    return ret

def run_backup(config_file, pass_hash_file):

    # reads config file
    r_cfg, v_cfg = read_config(config_file)
    if not r_cfg:
        print("%sFailed reading config file: [%s]%s" % (terminal_colors.TTY_RED, config_file, terminal_colors.get_standard_color()))
        return False

    # gets and checks the passphrase
    r_pp, passphrase = input_checked_passphrase.get_checked_passphrase(pass_hash_file)
    if not r_pp:
        print("%sHash doesn't check. Aborting...%s" % (terminal_colors.TTY_RED, terminal_colors.get_standard_color()))
        return False

    # call the backup engine
    bkeng = backup_engine.BackupEngine(v_cfg[0], make_backup_artifacts_list(v_cfg[1]), v_cfg[2], v_cfg[3], v_cfg[4], v_cfg[5], passphrase)
    bkeng_ret = bkeng.run()
    return bkeng_ret

def puaq(selfhelp):
    print("Usage: %s config_file pass_hash_file" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    config_file = sys.argv[1]
    pass_hash_file = sys.argv[2]

    v = run_backup(config_file, pass_hash_file)
    if not v:
        print("%sBackup failed. Config file: [%s]%s" % (terminal_colors.TTY_RED, config_file, terminal_colors.get_standard_color()))
        sys.exit(1)
