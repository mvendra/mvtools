#!/usr/bin/env python3

import sys
import os

import importlib.machinery
import importlib.util

import path_utils

def plug_filter(filter_details, target_path):

    if filter_details is None:
        return target_path

    loader = importlib.machinery.SourceFileLoader("plug_filter_%s" % path_utils.basename_filtered(filter_details[0]), filter_details[0]) # (partly) red meat
    spec = importlib.util.spec_from_loader(loader.name, loader) # pork
    mod = importlib.util.module_from_spec(spec) # pork
    loader.exec_module(mod) # pork

    return mod.filter_function(target_path, filter_details[1:])
