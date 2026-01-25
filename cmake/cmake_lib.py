#!/usr/bin/env python

import sys
import os

import path_utils
import cmake_wrapper

def boot_options():
    return {}

def set_option(options, option_name, option_type, option_value):
    if options is None:
        return None
    local_options = options.copy()
    local_options[option_name] = (option_type, option_value)
    return local_options.copy()

def set_option_parse(options, option_string):

    option_string_local = option_string

    option_name_local = None
    option_type_local = None
    option_value_local = None

    colon_pos = option_string_local.find(":")
    if colon_pos == -1:
        return None
    option_name_local = option_string_local[:colon_pos]
    option_string_local = option_string_local[colon_pos+1:]

    eq_sign_pos = option_string_local.find("=")
    if eq_sign_pos == -1:
        return None
    option_type_local = option_string_local[:eq_sign_pos]
    option_string_local = option_string_local[eq_sign_pos+1:]

    option_value_local = option_string_local

    return set_option(options, option_name_local, option_type_local, option_value_local)

def set_option_toolchain(options, option_value):
    return set_option(options, "CMAKE_TOOLCHAIN_FILE", "STRING", option_value)

def set_option_install_prefix(options, option_value):
    return set_option(options, "CMAKE_INSTALL_PREFIX", "STRING", option_value)

def set_option_prefix_path(options, option_value):
    return set_option(options, "CMAKE_PREFIX_PATH", "STRING", option_value)

def set_option_build_type(options, option_value):

    valid_values = ["debug", "release", "relwithdebinfo", "minsizerel"]

    if option_value is None:
        return None
    if not option_value.lower() in valid_values:
        return None

    return set_option(options, "CMAKE_BUILD_TYPE", "STRING", option_value)

def extract_options(cmake_path, source_path, output_path, temp_path):

    if os.path.exists(output_path):
        return False, "Output path [%s] already exists" % output_path

    v, r = cmake_wrapper.extract_options(cmake_path, source_path, temp_path, {})
    if not v:
        return False, r

    with open(output_path, "w") as f:
        f.write(r[1])

    return True, None

def configure_and_generate(cmake_path, source_path, output_path, generator_type, options):

    local_generator_type = generator_type

    # shortcuts / tricks
    if local_generator_type == "makefile":
        local_generator_type = "Unix Makefiles"
    elif local_generator_type == "ninja":
        local_generator_type = "Ninja"

    return cmake_wrapper.configure_and_generate(cmake_path, source_path, output_path, local_generator_type, options)

def build(cmake_path, target_path, parallel):
    return cmake_wrapper.build(cmake_path, target_path, parallel)

def install(cmake_path, target_path, prefix):
    return cmake_wrapper.install(cmake_path, target_path, prefix)
