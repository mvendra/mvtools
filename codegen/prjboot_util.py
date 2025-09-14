#!/usr/bin/env python

import sys
import os

from random import randrange

def secondary_c_app():
    return "\nvoid func(void);\n\nvoid func(void){}\n"

def makedir_if_needed(path):
    if not os.path.exists(path):
        os.mkdir(path)
        return True
    return False

def writecontents(filename, contents):
    if os.path.exists(filename):
        contents_read = ""
        with open(filename, "r") as f:
            contents_read = f.read()
        if contents == contents_read.strip():
            return True # file already exists, but its contents match the contents to be written - so it doesn't matter
        return False
    if not isinstance(contents, bytearray):
        contents_ba = bytearray()
        contents_ba.extend(map(ord, contents))
        contents = contents_ba
    with open(filename, "wb") as f:
        f.write(contents)
    return True

def add_to_gitignore_if_needed(gitignore_filename, new_content_line):

    # do not pass lists or multiline inputs on "new_content_line"

    if new_content_line == "":
        return
    if new_content_line.count("\n") != 0:
        return
    if isinstance(new_content_line, list):
        return

    new_contents = []

    if os.path.exists(gitignore_filename):

        read_contents = None
        with open(gitignore_filename, "r") as f:
            read_contents = f.read()

        new_contents = read_contents.split("\n")
        for l in new_contents:
            if l == new_content_line:
                return

    new_contents.append(new_content_line)

    assembled_contents = ""
    for i in range(len(new_contents)):
        pref = ""
        if i > 0:
            pref = "\n"
        assembled_contents += "%s%s" % (pref, new_contents[i])

    with open(gitignore_filename, "w") as f:
        f.write(assembled_contents)

def unroll_var(varname, varsign, list_source):

    if len(list_source) == 0:
        return ""

    local_contents = ""

    local_contents += "%s%s" % (varname, varsign)
    for opts in list_source:
        local_contents += "%s " % opts
    local_contents = local_contents.rstrip()

    return local_contents

def inline_opts(separator, list_source):

    if len(list_source) == 0:
        return ""

    local_contents = ""

    for i in range(len(list_source)):
        pref = ""
        if i > 0:
            pref = separator
        local_contents += "%s%s" % (pref, list_source[i])

    return local_contents

def filter_remove_dash_l(thestr):
    if len(thestr) < 3:
        return thestr
    if thestr[0:2] == "-l":
        return thestr[2:]
    return thestr

def format_xml_tag(indent, tag_name, tag_attrib, tag_value, value_filter_func):
    local_contents = ""
    local_contents = "%s<%s %s=\"%s\"/>" % (indent, tag_name, tag_attrib, value_filter_func(tag_value))
    return local_contents

def format_xml_tag_value_list(indent, tag_name, tag_attrib, list_source, value_filter_func):

    if len(list_source) == 0:
        return ""

    local_contents = ""

    for i in range(len(list_source)):
        pref = ""
        if i > 0:
            pref = "\n"
        local_contents += "%s%s" % (pref, format_xml_tag(indent, tag_name, tag_attrib, list_source[i], value_filter_func))

    return local_contents

def format_xml_tag_openclose(indent, tag_name, tag_internal_contents):
    local_contents = ""
    local_contents = "%s<%s>%s</%s>" % (indent, tag_name, tag_internal_contents, tag_name)
    return local_contents

def unroll_options_with_suffix(separator, suffix, list_source):
    local_contents = ""
    if len(list_source) == 0:
        return suffix
    for i in range(len(list_source)):
        pref = ""
        if i > 0:
            pref = separator
        local_contents += "%s%s" % (pref, list_source[i])
    local_contents += "%s%s" % (separator, suffix)
    return local_contents

def deco_if_not_empty(decorators_left, source_string, decorators_right):
    if source_string == "":
        return ""
    return "%s%s%s" % (decorators_left, source_string, decorators_right)

def gen_single_random_hex_digit():

    n = randrange(16)
    h = "%x" % n
    h_u = h.upper()
    return h_u

def random_32_hex_string_dashed():

    # example: "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"

    # first part
    dword_firstpart = ""
    for i in range(8):
        dword_firstpart += gen_single_random_hex_digit()

    # second part
    word_secondpart = ""
    for i in range(4):
        word_secondpart += gen_single_random_hex_digit()

    # third part
    word_thirdpart = ""
    for i in range(4):
        word_thirdpart += gen_single_random_hex_digit()

    # fourth part
    word_fourthpart = ""
    for i in range(4):
        word_fourthpart += gen_single_random_hex_digit()

    # fifth part
    tword_fifthpart = ""
    for i in range(12):
        tword_fifthpart += gen_single_random_hex_digit()

    full_string = "%s-%s-%s-%s-%s" % (dword_firstpart, word_secondpart, word_thirdpart, word_fourthpart, tword_fifthpart)
    return full_string
