#!/usr/bin/env python3

import sys
import os
import getpass
import shutil

import terminal_colors
import fsquery
import path_utils
import dsl_type20
import create_and_write_file
import dirsize

import tree_wrapper
import crontab_wrapper
import convert_unit
import collect_patches

class BackupPreparationException(RuntimeError):
    def __init__(self, msg):
        self._set_message(msg)
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

def derivefoldernamefortree(fullpath):

    """ derivefoldernamefortree
    takes a fullpath as input and returns a filename based off of it
    example: in: "/mnt/data/music" out: "music_tree_out.txt"
    """

    bn = path_utils.basename_filtered(fullpath).lower()
    return bn + "_tree_out.txt"

def derivefilenameforcrontab():
    username = getpass.getuser()
    return "crontab_" + username + ".txt"

class BackupPreparation:

    def __init__(self, _config_file):
        self.config_file = _config_file
        self.dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(True, True))
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
        v, r = self.dsl.get_all_variables()
        if not v:
            raise BackupPreparationException("Failed during setup: [%s]" % r)
        vars = dsl_type20.convert_var_obj_list_to_neutral_format(r)
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
            v, self.warn_size_each = convert_unit.convert_to_bytes(var_value)
            if not v:
                raise BackupPreparationException("Failed parsing, for SET_WARN_SIZE_EACH: %s" % var_value)
            if dsl_type20.hasopt_opts(var_options, "abort"):
                self.warn_size_each_abort = True

        elif var_name == "SET_WARN_SIZE_FINAL":
            self.warn_size_final_active = True
            v, self.warn_size_final = convert_unit.convert_to_bytes(var_value)
            if not v:
                raise BackupPreparationException("Failed parsing, for SET_WARN_SIZE_FINAL: %s" % var_value)
            if dsl_type20.hasopt_opts(var_options, "abort"):
                self.warn_size_final_abort = True

        else:
            return False # not handled
        return True # handled

    def do_copy_file(self, source_file, override_warn_size, override_warn_abort):

        if not os.path.exists(source_file):
            raise BackupPreparationException("[%s] does not exist." % source_file)

        warn_size_each_active_local = self.warn_size_each_active
        warn_size_each_local = self.warn_size_each
        warn_size_each_abort_local = self.warn_size_each_abort

        if override_warn_size is not None:
            warn_size_each_local = override_warn_size
            warn_size_each_active_local = True

        if override_warn_abort is not None:
            warn_size_each_abort_local = override_warn_abort
            warn_size_each_active_local = True

        target_candidate = path_utils.concat_path(self.storage_path, path_utils.basename_filtered(source_file))
        if os.path.exists(target_candidate):
            raise BackupPreparationException("[%s] already exists. Will not overwrite." % target_candidate)

        warn_msg = None
        if warn_size_each_active_local:
            if dirsize.get_dir_size(source_file, False) > warn_size_each_local:
                if warn_size_each_abort_local:
                    raise BackupPreparationException("[%s] is above the size limit. Aborting." % source_file)
                else:
                    warn_msg = "[%s] is above the size limit." % source_file

        path_utils.copy_to(source_file, self.storage_path)
        return warn_msg # mvtodo: must be printed in yellow, wherever it may

    def do_copy_content(self, content, target_filename):

        full_target_filename = path_utils.concat_path(self.storage_path, target_filename)
        if os.path.exists(full_target_filename):
            raise BackupPreparationException("[%s] already exists. Will not overwrite." % full_target_filename)

        warn_msg = None
        if self.warn_size_each_active:
            if len(content) > self.warn_size_each:
                if self.warn_size_each_abort:
                    raise BackupPreparationException("[%s] is above the size limit. Aborting." % target_filename)
                else:
                    warn_msg = "[%s] is above the size limit." % target_filename

        create_and_write_file.create_file_contents(full_target_filename, content)
        return warn_msg # mvtodo: must be printed in yellow, wherever it may

    def process_instructions(self):

        # does the second pass to process every single instruction
        for v in self.instructions:
            self.proc_single_inst(v[0], v[1], v[2])

        if self.warn_size_final_active:
            if dirsize.get_dir_size(self.storage_path, False) > self.warn_size_final:
                if self.warn_size_final_abort:
                    raise BackupPreparationException("The final folder [%s] is above the size limit. Aborting." % self.storage_path)
                else:
                    print("%sThe final folder [%s] is above the size limit.%s" % (terminal_colors.TTY_YELLOW_BOLD, self.storage_path, terminal_colors.TTY_WHITE)) # mvtodo

    def proc_single_inst(self, var_name, var_value, var_options):

        # reminder: when implementing new instructions, always consider using the internal, helper
        # functions ("do_copy_file" and "do_copy_content") because they concentrate the warning system
        # feature (checking for excessive filesizes) and also the storage path handling.

        if var_name == "COPY_PATH":
            self.proc_copy_path(var_value, var_options)
        elif var_name == "COPY_PATH_TO":
            self.proc_copy_path_to(var_value, var_options)
        elif var_name == "COPY_TREE_OUT":
            self.proc_copy_tree_out(var_value, var_options)
        elif var_name == "COPY_SYSTEM":
            self.proc_copy_system(var_value, var_options)
        elif var_name == "RUN_COLLECT_PATCHES":
            self.proc_run_collect_patches(var_value, var_options)
        else:
            raise BackupPreparationException("Invalid instruction: [%s] [%s] [%s]. Aborting." % (var_name, var_value, var_options))

    def proc_copy_path(self, var_value, var_options):

        # sanitizes origin_path: paths ending in path separator fail from here on. so lets just remove it.
        origin_path = path_utils.filter_remove_trailing_sep(var_value)

        if not os.path.exists(origin_path):
            if dsl_type20.hasopt_opts(var_options, "abort"):
                raise BackupPreparationException("[%s] does not exist. Aborting." % origin_path)
            else:
                return "[%s] does not exist. Skipping." % origin_path # mvtodo: must be printed in yellow, wherever it may

        override_warn_size = None
        override_warn_abort = None

        for o in var_options:
            if o[0] == "warn_size":
                cb = convert_unit.convert_to_bytes(o[1])
                if not cb[0]:
                    raise BackupPreparationException("Failed parsing: [%s]. Aborting." % o[1])
                override_warn_size = cb[1]
            elif o[0] == "warn_abort":
                override_warn_abort = True

        return self.do_copy_file(origin_path, override_warn_size, override_warn_abort)

    def proc_copy_path_to(self, var_value, var_options):

        dest_path = path_utils.filter_remove_trailing_sep(var_value)

        if not dsl_type20.hasopt_opts(var_options, "source"):
            raise BackupPreparationException("Source path option is missing. Aborting.")
        if not os.path.exists(dest_path):
            raise BackupPreparationException("Dest path [%s] does not exist. Aborting." % dest_path)
        if not os.path.isdir(dest_path):
            raise BackupPreparationException("Dest path [%s] is not a directory. Aborting." % dest_path)

        source_path = None
        for o in var_options:
            if o[0] == "source":
                source_path = o[1]

        if not os.path.exists(source_path):
            raise BackupPreparationException("Source path [%s] does not exist. Aborting." % source_path)

        path_utils.copy_to(source_path, dest_path)

    def proc_copy_tree_out(self, var_value, var_options):

        v, r = tree_wrapper.make_tree(var_value)
        if not v:
            if dsl_type20.hasopt_opts(var_options, "abort"):
                raise BackupPreparationException("Failed generating tree for [%s]: [%s]. Aborting." % (var_value, r))
            else:
                return "Failed generating tree for [%s]: [%s]. Skipping." % (var_value, r) # mvtodo: must be printed in yellow, wherever it may

        self.do_copy_content(r, derivefoldernamefortree(var_value))

    def proc_copy_system(self, var_value, var_options):

        if var_value == "crontab":

            v, r = crontab_wrapper.get_crontab()
            if not v:
                if dsl_type20.hasopt_opts(var_options, "abort"):
                    raise BackupPreparationException("Failed retrieving user's crontab. Aborting.")
                else:
                    return "Failed retrieving user's crontab. Skipping." # mvtodo: must be printed in yellow, wherever it may

            self.do_copy_content(r, derivefilenameforcrontab())

        else:
            raise BackupPreparationException("Invalid COPY_SYSTEM value: [%s] [%s]. Aborting." % (var_value, var_options))

    def proc_run_collect_patches(self, var_value, var_options):

        # do the pre-parsing
        custom_path_navigator_script = None
        custom_path_navigator_func = None
        source_path = ""
        storage_base = ""
        repo_type = ""
        default_filter = ""
        includes = []
        excludes = []
        default_subfilter = ""
        subfilter_includes = []
        subfilter_excludes = []
        head = False
        head_id = False
        staged = False
        unversioned = False
        stash = False
        cherry_pick_previous = None
        previous = 0

        # source path
        source_path = var_value

        for o in var_options:
            opt_name, opt_val = o

            # custom path navigator
            if opt_name == "custom-path-navigator":
                if opt_val is None or opt_val == "":
                    raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options (can't parse \"custom-path-navigator\"): [%s]. Aborting." % (var_options))
                custom_path_navigator_script = opt_val

            # storage path
            if opt_name == "storage-base":
                storage_base = opt_val

            # repo type
            if opt_name == "svn":
                repo_type = "svn"
            if opt_name == "git":
                repo_type = "git"
            if opt_name == "all":
                repo_type = "all"

            # default filter
            if opt_name == "default-include":
                default_filter = "include"
            if opt_name == "default-exclude":
                default_filter = "exclude"

            # includes / excludes
            if opt_name == "include":
                if opt_val is None or opt_val == "":
                    raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options (can't parse \"include\"): [%s]. Aborting." % (var_options))
                if isinstance(opt_val, list):
                    includes += opt_val
                else:
                    includes.append(opt_val)
            if opt_name == "exclude":
                if opt_val is None or opt_val == "":
                    raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options (can't parse \"exclude\"): [%s]. Aborting." % (var_options))
                if isinstance(opt_val, list):
                    excludes += opt_val
                else:
                    excludes.append(opt_val)

            # default subfilter
            if opt_name == "default-subfilter-include":
                default_subfilter = "include"
            if opt_name == "default-subfilter-exclude":
                default_subfilter = "exclude"

            # subfilter includes / excludes
            if opt_name == "subfilter-include":
                if opt_val is None or opt_val == "":
                    raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options (can't parse \"subfilter-include\"): [%s]. Aborting." % (var_options))
                if isinstance(opt_val, list):
                    subfilter_includes += opt_val
                else:
                    subfilter_includes.append(opt_val)
            if opt_name == "subfilter-exclude":
                if opt_val is None or opt_val == "":
                    raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options (can't parse \"subfilter-exclude\"): [%s]. Aborting." % (var_options))
                if isinstance(opt_val, list):
                    subfilter_excludes += opt_val
                else:
                    subfilter_excludes.append(opt_val)

            # collection options
            if opt_name == "head":
                head = True
            if opt_name == "head-id":
                head_id = True
            if opt_name == "staged":
                staged = True
            if opt_name == "unversioned":
                unversioned = True
            if opt_name == "stash":
                try:
                    stash = int(opt_val)
                except:
                    raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options (can't parse \"stash\"): [%s]. Aborting." % (var_options))
            if opt_name == "cherry-pick-previous":
                cherry_pick_previous = opt_val
            if opt_name == "previous":
                try:
                    previous = int(opt_val)
                except:
                    raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options (can't parse \"previous\"): [%s]. Aborting." % (var_options))

        # resolve custom path navigator function
        if custom_path_navigator_script is not None:
            custom_path_navigator_probe = collect_patches.resolve_py_into_custom_pathnav_func(custom_path_navigator_script)
            if custom_path_navigator_probe is None:
                raise BackupPreparationException("Invalid RUN_COLLECT_PATCHES options - the custom navigation script [%s] cannot be loaded. Aborting." % (custom_path_navigator_script))

        # guarantee the storage folder
        final_storage_path_patch_collector = path_utils.concat_path(self.storage_path, storage_base)
        if not path_utils.guaranteefolder(final_storage_path_patch_collector):
            raise BackupPreparationException("Unable to guarantee folder [%s]." % (final_storage_path_patch_collector))

        # run the actual patch collector
        v, r = collect_patches.collect_patches(source_path, custom_path_navigator_script, final_storage_path_patch_collector, default_filter, includes, excludes, default_subfilter, subfilter_includes, subfilter_excludes, head, head_id, staged, unversioned, stash, previous, cherry_pick_previous, repo_type)
        if not v:
            for i in r:
                print("proc_run_collect_patches: [%s]" % i)

def backup_preparation(config_file):

    bkprep = BackupPreparation(config_file)
    try:
        bkprep.run_preparation()
    except BackupPreparationException as bpe:    
        print("%sFailed processing [%s]: %s%s" % (terminal_colors.TTY_RED, config_file, bpe._get_message(), terminal_colors.TTY_WHITE))
        return False

    return True

def puaq():
    print("Usage: %s config_file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    config_file = sys.argv[1]

    print("Preparation begins...")
    if not backup_preparation(config_file):
        sys.exit(1)
    print("%sPreparation is complete.%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
