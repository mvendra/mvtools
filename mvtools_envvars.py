#!/usr/bin/env python3

import sys
import os

import path_utils

class Mvtools_Envvars:

    def __init__(self):
        self.MVTOOLS_ENVVARS = {}
        self.ENVIRON_COPY = None

        # register more mvtools envvars here
        self.register_mvtools_envvar("MVTOOLS")
        self.register_mvtools_envvar("MVTOOLS_TEMP_PATH")
        self.register_mvtools_envvar("MVTOOLS_LINKS_PATH")
        self.register_mvtools_envvar("MVTOOLS_TOOLBUS_BASE")
        self.register_mvtools_envvar("MVTOOLS_GIT_VISITOR_BASE")
        self.register_mvtools_envvar("MVTOOLS_CYGWIN_INSTALL_PATH")
        self.register_mvtools_envvar("MVTOOLS_PIP_VENV_INSTALL_PATH")

        self.register_mvtools_envvar("MVTOOLS_TEST_GENERIC_RUN_RESERVED_1")
        self.register_mvtools_envvar("MVTOOLS_TEST_DSLTYPE20_RESERVED_1")
        self.register_mvtools_envvar("MVTOOLS_TEST_DSLTYPE20_RESERVED_2")
        self.register_mvtools_envvar("MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_1")
        self.register_mvtools_envvar("MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_2")
        self.register_mvtools_envvar("MVTOOLS_TEST_BKPROC_RESERVED_1")

    def _read_envvar(self, envvar):
        envvar_val = ""
        try:
            envvar_val = os.environ[self.MVTOOLS_ENVVARS[envvar]]
        except KeyError:
            return False, "Failed retrieving envvar [%s]" % envvar
        return True, envvar_val

    def _write_envvar(self, envvar, val):
        if not envvar in self.MVTOOLS_ENVVARS:
            return False, "Failed writing to envvar [%s]: not previously registered" % (envvar)
        if val is None or val == "":
            return False, "Failed writing to envvar [%s]: value [%s] is invalid" % (envvar, val)
        os.environ[self.MVTOOLS_ENVVARS[envvar]] = val
        return True, None

    def register_mvtools_envvar(self, envvar):
        self.MVTOOLS_ENVVARS[envvar] = envvar

    def list_mvtools_envvar(self):
        ret = []
        for k in self.MVTOOLS_ENVVARS:
            ret.append(k)
        return ret

    def make_copy_environ(self):
        if self.ENVIRON_COPY is not None:
            return False, "There is already a living copy of the environ."
        self.ENVIRON_COPY = os.environ.copy()
        return True, None

    def restore_copy_environ(self):
        if self.ENVIRON_COPY is None:
            return False, "There is no living copy of the environ."
        os.environ.clear()
        os.environ.update(self.ENVIRON_COPY)
        self.ENVIRON_COPY = None
        return True, None

# module's public interface:

# MVTOOLS
def mvtools_envvar_read_main():
    return Mvtools_Envvars()._read_envvar("MVTOOLS")
def mvtools_envvar_write_main(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS", val)

# MVTOOLS_TEMP_PATH
def mvtools_envvar_read_temp_path():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TEMP_PATH")
def mvtools_envvar_write_temp_path(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TEMP_PATH", val)

# MVTOOLS_LINKS_PATH
def mvtools_envvar_read_links_path():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_LINKS_PATH")
def mvtools_envvar_write_links_path(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_LINKS_PATH", val)

# MVTOOLS_TOOLBUS_BASE
def mvtools_envvar_read_toolbus_base():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TOOLBUS_BASE")
def mvtools_envvar_write_toolbus_base(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TOOLBUS_BASE", val)

# MVTOOLS_GIT_VISITOR_BASE
def mvtools_envvar_read_git_visitor_base():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_GIT_VISITOR_BASE")
def mvtools_envvar_write_git_visitor_base(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_GIT_VISITOR_BASE", val)

# MVTOOLS_CYGWIN_INSTALL_PATH
def mvtools_envvar_read_cygwin_install_path():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_CYGWIN_INSTALL_PATH")
def mvtools_envvar_write_cygwin_install_path(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_CYGWIN_INSTALL_PATH", val)

# MVTOOLS_PIP_VENV_INSTALL_PATH
def mvtools_envvar_read_pip_venv_install_path():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_PIP_VENV_INSTALL_PATH")
def mvtools_envvar_write_pip_venv_install_path(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_PIP_VENV_INSTALL_PATH", val)

# MVTOOLS_TEST_GENERIC_RUN_RESERVED_1
def mvtools_envvar_read_test_generic_run_reserved_1():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TEST_GENERIC_RUN_RESERVED_1")
def mvtools_envvar_write_test_generic_run_reserved_1(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TEST_GENERIC_RUN_RESERVED_1", val)

# MVTOOLS_TEST_DSLTYPE20_RESERVED_1
def mvtools_envvar_read_test_dsltype20_reserved_1():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TEST_DSLTYPE20_RESERVED_1")
def mvtools_envvar_write_test_dsltype20_reserved_1(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TEST_DSLTYPE20_RESERVED_1", val)

# MVTOOLS_TEST_DSLTYPE20_RESERVED_2
def mvtools_envvar_read_test_dsltype20_reserved_2():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TEST_DSLTYPE20_RESERVED_2")
def mvtools_envvar_write_test_dsltype20_reserved_2(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TEST_DSLTYPE20_RESERVED_2", val)

# MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_1
def mvtools_envvar_read_test_check_envvars_plugin_reserved_1():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_1")
def mvtools_envvar_write_test_check_envvars_plugin_reserved_1(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_1", val)

# MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_2
def mvtools_envvar_read_test_check_envvars_plugin_reserved_2():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_2")
def mvtools_envvar_write_test_check_envvars_plugin_reserved_2(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_2", val)

# MVTOOLS_TEST_BKPROC_RESERVED_1
def mvtools_envvar_read_test_bkproc_reserved_1():
    return Mvtools_Envvars()._read_envvar("MVTOOLS_TEST_BKPROC_RESERVED_1")
def mvtools_envvar_write_test_bkproc_reserved_1(val):
    return Mvtools_Envvars()._write_envvar("MVTOOLS_TEST_BKPROC_RESERVED_1", val)

if __name__ == "__main__":

    print("Hello from %s. Mvtool's envvars are:" % path_utils.basename_filtered(__file__))
    for e in Mvtools_Envvars().list_mvtools_envvar():
        print(e)
