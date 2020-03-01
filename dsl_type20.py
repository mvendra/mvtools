#!/usr/bin/env python3

import sys
import os

import miniparse

# class for parsing "dsl type 20"
# samples:
# variable1 = "value1"
# variable2 {option1} = "value2"
# variable3 {option2 / option3: "value3"} = "value4"
#
# lines starting with "#" are skipped (treated as comment).
# lines are string-trimmed (extra spaces are removed)
# variable names and optins can be repeated

class DSLType20:
    def __init__(self):
        self.clear()

    def clear(self):
        self.data = []

    def parse(self, contents):

        self.clear()

        lines = contents.split("\n")
        for line in lines:
            line_t = line.strip()
            if line_t == "":
                continue
            if line_t[0] == "#":
                continue

            in_split = miniparse.guarded_split(line_t, "=", [("{", "}"), ("\"","\"")])
            if len(in_split) != 2:
                return False, "String [%s] can't be parsed." % line_t
            var_name_and_options, var_value = in_split
            var_name_and_options = var_name_and_options.strip()
            var_value = var_value.strip()

            var_name = ""
            var_options = ""

            p = var_name_and_options.find("{")
            if p == -1:
                var_name = var_name_and_options
            else:
                var_name = (var_name_and_options[0:p]).strip()
                var_options = (var_name_and_options[p:]).strip()

            var_value_pre = var_value
            bp, var_value = miniparse.pop_surrounding_char(var_value, "\"", "\"")
            # require values to be specified with surrounding quotes
            if bp is False:
                return False, "Value must be specified with surrounding quotes: [%s]" % var_value_pre

            # separate options
            options_pre = (miniparse.pop_surrounding_char(var_options, "{", "}"))[1].strip()
            options = miniparse.guarded_split(options_pre, "/", [("\"","\"")])
            for i in range(len(options)):
                options[i] = options[i].strip()

            # parse options, names x values
            parsed_opts = []
            for o in options:
                opt_name, opt_val = miniparse.opt_get(o, ":")
                parsed_opts.append( (opt_name, opt_val) )

            if var_name == "":
                return False, "Empty var name: [%s]" % line_t

            if var_value == "":
                return False, "Empty var value: [%s]" % line_t

            self.data.append( (var_name, var_value, parsed_opts) )

        return True, None

    def getvars(self, varname):
        ret = []
        for v in self.data:
            if v[0] == varname:
                ret.append(v)
        return ret

    def getopts(self, var, optname):
        ret = []
        for o in var[2]:
            if o[0] == optname:
                ret.append(o)
        return ret

    def hasopt(self, var, optname):
        for o in var[2]:
            if o[0] == optname:
                return True
        return False
