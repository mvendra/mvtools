#!/usr/bin/env python3

import sys
import os
import getpass

import terminal_colors
import fsquery
import path_utils
import dsl_type20
import create_and_write_file
import dirsize

import tree_wrapper
import crontab_wrapper

class BackupPreparationException(RuntimeError):
    def __init__(self, msg):
        self._set_message(msg)
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

def convert_to_bytes(size_string):

    try:
        s_number = ""
        s_unit = ""
        multiplier = 1

        if len(size_string) < 3:
            return (True, int(size_string))

        s_number = size_string[0:len(size_string)-2]
        s_unit = size_string[len(size_string)-2:]
        s_unit = s_unit.lower()

        if s_unit == "kb":
            multiplier = 1024
        elif s_unit == "mb":
            multiplier = 1024*1024
        elif s_unit == "gb":
            multiplier = 1024*1024*1024
        elif s_unit == "tb":
            multiplier = 1024*1024*1024*1024
        else:
            s_number = size_string

        final_num = int(s_number) * multiplier
        return (True, final_num)
    except:
        return (False, None)

def derivefoldernamefortree(fullpath):

    """ derivefoldernamefortree
    takes a fullpath as input and returns a filename based off of it
    example: in: "/mnt/data/music" out: "music_tree_out.txt"
    """

    bn = os.path.basename(fullpath).lower()
    return bn + "_tree_out.txt"

def derivefilenameforcrontab():
    username = getpass.getuser()
    return "crontab_" + username + ".txt"

class BackupPreparation:

    def __init__(self, _config_file):
        self.config_file = _config_file
        self.dsl = dsl_type20.DSLType20(True, True)
        self.instructions = [] # the instructions only, without the config/setup variables

        # default configs
        self.storage_path = ""
        self.storage_path_reset = False

        self.warn_size_each_active = False
        self.warn_size_each = 0
        self.warn_size_each_abort = False

        self.warn_size_final_active = False
        self.warn_size_final = 0
        self.warn_size_final_abort = False

    def run_preparation(self):

        # load file and parse
        self.read_config(self.config_file)

        # first pass (configuration)
        self.setup_configuration()

        # second pass (instructions)
        self.process_instructions()

    def read_config(self, config_file):

        # checks if the file exists
        if not os.path.exists(config_file):
            raise BackupPreparationException("Config file does not exist.")

        # read file contents
        cfg_contents = ""
        with open(config_file) as f:
            cfg_contents = f.read()

        # parses into dsl class
        v, r = self.dsl.parse(cfg_contents)
        if not v:
            raise BackupPreparationException("Failed parsing: %s" % r)

    def setup_configuration(self):

        # does the first pass to setup the configuration
        vars = self.dsl.getallvars()
        for v in vars:
            p = self.proc_single_config(v[0], v[1], v[2])
            if not p:
                # not handled by configuration. likely an instruction. separate it from the config variables
                # so false instructions can be detected
                self.instructions.append(v)

        # now process the configuration variables
        if self.storage_path_reset:
            path_utils.scratchfolder(self.storage_path)
        if not os.path.exists(self.storage_path):
            raise BackupPreparationException("Storage path [%s] does not exist." % self.storage_path)

    def proc_single_config(self, var_name, var_value, var_options):

        if var_name == "SET_STORAGE_PATH":
            self.storage_path = var_value
            if dsl_type20.hasopt_opts(var_options, "reset"):
                self.storage_path_reset = True

        elif var_name == "SET_WARN_SIZE_EACH":
            self.warn_size_each_active = True
            v, self.warn_size_each = convert_to_bytes(var_value)
            if not v:
                raise BackupPreparationException("Failed parsing, for SET_WARN_SIZE_EACH: %s" % var_value)
            if dsl_type20.hasopt_opts(var_options, "abort"):
                self.warn_size_each_abort = True

        elif var_name == "SET_WARN_SIZE_FINAL":
            self.warn_size_final_active = True
            v, self.warn_size_final = convert_to_bytes(var_value)
            if not v:
                raise BackupPreparationException("Failed parsing, for SET_WARN_SIZE_FINAL: %s" % var_value)
            if dsl_type20.hasopt_opts(var_options, "abort"):
                self.warn_size_final_abort = True

        else:
            return False # not handled
        return True # handled

    def do_copy_file(self, source_file):

        target_candidate = path_utils.concat_path(self.storage_path, os.path.basename(source_file))
        if os.path.exists(target_candidate):
            raise BackupPreparationException("[%s] already exists. Will not overwrite." % target_candidate)

        if self.warn_size_each_active:
            if dirsize.get_dir_size(source_file, False) > self.warn_size_each:
                if self.warn_size_each_abort:
                    raise BackupPreparationException("[%s] is above the size limit. Aborting." % source_file)
                else:
                    print("%s[%s] is above the size limit.%s" % (terminal_colors.TTY_YELLOW_BOLD, source_file, terminal_colors.TTY_WHITE))

        path_utils.copy_to(source_file, self.storage_path)

    def do_copy_content(self, content, target_filename):

        full_target_filename = path_utils.concat_path(self.storage_path, target_filename)
        if os.path.exists(full_target_filename):
            raise BackupPreparationException("[%s] already exists. Will not overwrite." % full_target_filename)

        if self.warn_size_each_active:
            if len(content) > self.warn_size_each:
                if self.warn_size_each_abort:
                    raise BackupPreparationException("[%s] is above the size limit. Aborting." % target_filename)
                else:
                    print("%s[%s] is above the size limit.%s" % (terminal_colors.TTY_YELLOW_BOLD, target_filename, terminal_colors.TTY_WHITE))

        create_and_write_file.create_file_contents(full_target_filename, content)

    def process_instructions(self):

        # does the second pass to process every single instruction
        for v in self.instructions:
            self.proc_single_inst(v[0], v[1], v[2])

        if self.warn_size_final_active:
            if dirsize.get_dir_size(self.storage_path, False) > self.warn_size_final:
                if self.warn_size_final_abort:
                    raise BackupPreparationException("The final folder [%s] is above the size limit. Aborting." % self.storage_path)
                else:
                    print("%sThe final folder [%s] is above the size limit.%s" % (terminal_colors.TTY_YELLOW_BOLD, self.storage_path, terminal_colors.TTY_WHITE))

    def proc_single_inst(self, var_name, var_value, var_options):

        # reminder: when implementing new instructions, always consider using the internal, helper
        # functions ("do_copy_file" and "do_copy_content") because they concentrate the warning system
        # feature (checking for excessive filesizes) and also the storage path handling.

        if var_name == "COPY_PATH":
            self.proc_copy_path(var_value, var_options)
        elif var_name == "COPY_TREE_OUT":
            self.proc_copy_tree_out(var_value, var_options)
        elif var_name == "COPY_SYSTEM":
            self.proc_copy_system(var_value, var_options)
        else:
            raise BackupPreparationException("Invalid instruction: [%s] [%s] [%s]. Aborting." % (var_name, var_value, var_options))

    def proc_copy_path(self, var_value, var_options):

        origin_path = var_value
        if not os.path.exists(origin_path):
            if dsl_type20.hasopt_opts(var_options, "abort"):
                raise BackupPreparationException("[%s] does not exist. Aborting." % origin_path)
            else:
                print("%s[%s] does not exist. Skipping.%s" % (terminal_colors.TTY_YELLOW_BOLD, origin_path, terminal_colors.TTY_WHITE))
                return

        self.do_copy_file(origin_path)

    def proc_copy_tree_out(self, var_value, var_options):

        v, r = tree_wrapper.make_tree(var_value)
        if not v:
            if dsl_type20.hasopt_opts(var_options, "abort"):
                raise BackupPreparationException("Failed generating tree for [%s]: [%s]. Aborting." % (var_value, r))
            else:
                print("%sFailed generating tree for [%s]: [%s]. Skipping.%s" % (terminal_colors.TTY_YELLOW_BOLD, var_value, r, terminal_colors.TTY_WHITE))
                return

        self.do_copy_content(r, derivefoldernamefortree(var_value))

    def proc_copy_system(self, var_value, var_options):

        if var_value == "crontab":
            v, r = crontab_wrapper.get_crontab()
            if not v:
                if dsl_type20.hasopt_opts(var_options, "abort"):
                    raise BackupPreparationException("Failed retrieving user's crontab. Aborting.")
                else:
                    print("%sFailed retrieving user's crontab. Skipping.%s" % (terminal_colors.TTY_YELLOW_BOLD, terminal_colors.TTY_WHITE))
                    return

            self.do_copy_content(r, derivefilenameforcrontab())

        else:
            raise BackupPreparationException("Invalid COPY_SYSTEM value: [%s] [%s]. Aborting." % (var_value, var_options))

def backup_preparation(config_file):

    bkprep = BackupPreparation(config_file)
    try:
        bkprep.run_preparation()
    except BackupPreparationException as bpe:    
        print("%sFailed processing [%s]: %s%s" % (terminal_colors.TTY_RED, config_file, bpe._get_message(), terminal_colors.TTY_WHITE))
        return False

    return True

def puaq():
    print("Usage: %s config_file" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    config_file = sys.argv[1]

    print("Preparation begins...")
    if not backup_preparation(config_file):
        sys.exit(1)
    print("%sPreparation is complete.%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
