#!/usr/bin/env python3

import sys
import os

import terminal_colors
import fsquery
import path_utils
import dsl_type20
import create_and_write_file

import tree_wrapper

class BackupPreparationException(RuntimeError):
    def __init__(self, msg):
        self._set_message(msg)
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

def convert_to_bytes(size_string):
    return 21 # mvtodo

def derivefoldernamefortree(fullpath):

    """ derivefoldernamefortree
    takes a fullpath as input and returns a filename based off of it
    example: in: "/mnt/data/music" out: "music_tree_out.txt"
    """

    bn = os.path.basename(fullpath).lower()
    return bn + "_tree_out.txt"

class BackupPreparation:

    def __init__(self, _config_file):
        self.config_file = _config_file
        self.dsl = dsl_type20.DSLType20(True, True)

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
            v = self.proc_single_config(v[0], v[1], v[2])

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
            self.warn_size_each = convert_to_bytes(var_value)
            if dsl_type20.hasopt_opts(var_options, "abort"):
                self.warn_size_each_abort = True

        elif var_name == "SET_WARN_SIZE_FINAL":
            self.warn_size_final = convert_to_bytes(var_value)
            if dsl_type20.hasopt_opts(var_options, "abort"):
                self.warn_size_final_abort = True

    def process_instructions(self):

        # does the second pass to process every single instruction
        vars = self.dsl.getallvars()
        for v in vars:
            self.proc_single_inst(v[0], v[1], v[2])

    def proc_single_inst(self, var_name, var_value, var_options):

        if var_name == "COPY_PATH":
            self.proc_copy_path(var_value, var_options)
        elif var_name == "COPY_TREE_OUT":
            self.proc_copy_tree_out(var_value, var_options)

    def proc_copy_path(self, var_value, var_options):
        origin_path = var_value
        if not os.path.exists(origin_path):
            if dsl_type20.hasopt_opts(var_options, "abort"):
                raise BackupPreparationException("[%s] does not exist. Aborting." % origin_path)
            else:
                return

        target_candidate = path_utils.concat_path(self.storage_path, os.path.basename(origin_path))
        if os.path.exists(target_candidate):
            raise BackupPreparationException("[%s] already exists. Will not overwrite." % target_candidate)
        path_utils.copy_to(origin_path, self.storage_path)

    def proc_copy_tree_out(self, var_value, var_options):
        v, r = tree_wrapper.make_tree(var_value)

        if not v:
            if dsl_type20.hasopt_opts(var_options, "abort"):
                raise BackupPreparationException("Failed generating tree for [%s]: [%s]" % (var_value, r))
            else:
                return

        tree_out_file = path_utils.concat_path(self.storage_path, derivefoldernamefortree(var_value))
        create_and_write_file.create_file_contents(tree_out_file, r)

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
