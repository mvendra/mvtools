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

def getopts(var, optname):
    ret = []
    for o in var[2]:
        if o[0] == optname:
            ret.append(o)
    return ret

def hasopt_var(var, optname):
    for o in var[2]:
        if o[0] == optname:
            return True
    return False

def hasopt_opts(opts, optname):
    for o in opts:
        if o[0] == optname:
            return True
    return False

class DSLType20:
    def __init__(self, _expand_envvars, _expand_user):
        self.expand_envvars = _expand_envvars
        self.expand_user = _expand_user
        self.clear()

    def clear(self):
        self.data = []

    def _expand(self, str_input):

        local_str_input = str_input

        if self.expand_envvars:
            local_str_input = os.path.expandvars(local_str_input)
            if "$" in local_str_input:
                return False, str_input

        if self.expand_user:
            local_str_input = os.path.expanduser(local_str_input)
            if "~" in local_str_input:
                return False, str_input

        return True, local_str_input

    def sanitize_line(self, line_in):

        line_out = line_in.strip()

        hash_pos = line_out.find("#")
        if hash_pos != -1:
            line_out = line_out[0:hash_pos]

        return line_out.strip()

    def parse(self, contents):

        self.clear()

        lines = contents.split("\n")
        for line in lines:

            line_t = self.sanitize_line(line)
            if line_t == "":
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

            v, r = self._expand(var_value)
            if not v:
                return False, "Variable expansion failed: [%s]" % var_value
            var_value = r

            # separate options
            options_pre = (miniparse.pop_surrounding_char(var_options, "{", "}"))[1].strip()
            options = miniparse.guarded_split(options_pre, "/", [("\"","\"")])
            for i in range(len(options)):
                options[i] = options[i].strip()

            # parse options, names x values
            parsed_opts = []
            for o in options:
                opt_name, opt_val = miniparse.opt_get(o, ":")
                if opt_name is None and opt_val is not None:
                    return False, "Malformed option name: [%s]" % o
                if opt_name is not None and opt_val is None:
                    return False, "Malformed option value: [%s]" % o
                v, r = self._expand(opt_val)
                if not v:
                    return False, "Variable expansion failed: [%s]" % opt_val
                opt_val = r
                parsed_opts.append( (opt_name, opt_val) )

            if var_name == "":
                return False, "Empty var name: [%s]" % line_t

            if var_value == "":
                return False, "Empty var value: [%s]" % line_t

            self.data.append( (var_name, var_value, parsed_opts) )

        return True, None

    def getallvars(self):
        return self.data

    def getvars(self, varname):
        ret = []
        for v in self.data:
            if v[0] == varname:
                ret.append(v)
        return ret
