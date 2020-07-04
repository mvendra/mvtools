#!/usr/bin/env python3

import sys
import os

import miniparse

# class for parsing "dsl type 20"
# samples:
# variable1 = "value1" # quotes are mandatory for values
# variable1 = "value \"1\"" # quotes inside values must be escaped with "\"
# variable1 = "value \\2" # the escape character "\" itself has to be escaped
# variable2 {option1} = "value2"
# variable3 {option2 / option3: "value3"} = "value4"
# variable4 {option4: "value \"3\""} = "value \"5\"" # again, escaping quotes is necessary wherever you have a value
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

        self.VAR_ID = "[_\\-a-zA-Z0-9]+"
        self.ANYSPACE = "[ ]*"
        self.COLON = ":"
        self.AT_SIGN = "@"
        self.LCBRACKET = "["
        self.RCBRACKET = "]"
        self.LCBRACKET = "{"
        self.RCBRACKET = "}"
        self.EQ_SIGN = "="
        self.QUOTE = "\""
        self.BSLASH = "\\"
        self.FSLASH = "/"

        self.max_number_options = 1024

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

            v, r = self.parse_variable(line_t)
            if not v:
                return v, r

        return True, None

    def parse_variable(self, str_input):

        var_name = None
        var_value = None
        var_options = None
        parsed_opts = []

        local_str_input = str_input.strip()

        # start by parsing the variable's value
        v, r = miniparse.scan_and_slice_end(local_str_input, self.QUOTE)
        if not v:
            return False, "Malformed variable: [%s]: value must be be enclosed with quotes." % str_input
        if r[1][len(r[1])-1] == self.BSLASH: # variable value was indeed enclosed with quotes, but the last quote was escaped. error.
            return False, "Malformed variable: [%s]: value must be be enclosed with a nonescaped quote (failed at the second quote)." % str_input
        local_str_input = r[1]

        # find next nonescaped quote in reverse (beginning of the value)
        v, r = miniparse.last_not_escaped_slice(local_str_input, self.QUOTE, self.BSLASH)
        if not v:
            return False, "Malformed variable: [%s]: can't find first quote of the variable's value." % str_input
        local_str_input = (r[1]).strip()
        var_value = r[0]

        # descape the variable's value
        v, r = miniparse.descape(var_value, self.BSLASH)
        if not v:
            return False, "Variable descaping failed: [%s]" % var_value
        var_value = r

        # expand the variable's value
        v, r = self._expand(var_value)
        if not v:
            return False, "Variable expansion failed: [%s]" % var_value
        var_value = r

        # remove first quote of value
        v, r = miniparse.scan_and_slice_end(local_str_input, self.QUOTE)
        if not v:
            return False, "Malformed variable: [%s]: value must be be enclosed with quotes." % str_input
        local_str_input = (r[1]).strip()

        # leave in the equal sign so further parsing can detect syntax problems

        v, r = miniparse.scan_and_slice_beginning(local_str_input, self.VAR_ID + self.ANYSPACE + self.LCBRACKET)
        if v:

            # variable has options

            var_name = r[0].strip()
            local_str_input = r[1].strip()

            v, r = miniparse.remove_last_of(var_name, self.LCBRACKET)
            if not v:
                return False, "Malformed variable: [%s]: Failed removing left bracket from options." % str_input
            var_name = r.strip()

            # parse the options
            v, r1, r2 = self.parse_variable_options(local_str_input)
            if not v:
                return False, "Failed parsing options: [%s]: [%s]" % (var_options, r1)
            parsed_opts = r1
            local_str_input = r2

            # remove the eq sign from the tail
            v, r = miniparse.remove_last_of(local_str_input, self.EQ_SIGN)
            if not v:
                return False, "Malformed variable: [%s]: Failed removing equal sign from tail." % str_input
            local_str_input = r.strip()

            if len(local_str_input) != 0:
                return False, "Malformed variable: [%s]: Remaining unparseable contents: [%s]." % (str_input, local_str_input)

        else:

            # variable has no options

            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.VAR_ID + self.ANYSPACE + self.EQ_SIGN)
            if not v:
                return False, "Malformed variable: [%s]: Can't parse variable name." % str_input
            var_name = (r[0]).strip()
            local_str_input = (r[1]).strip()

            # remove the eq sign from name
            v, r = miniparse.remove_last_of(var_name, self.EQ_SIGN)
            if not v:
                return False, "Malformed variable: [%s]: Failed removing equal sign from name." % str_input
            var_name = r.strip()

            if len(local_str_input) != 0:
                return False, "Malformed variable: [%s]: Remaining unparseable contents: [%s]." % (str_input, local_str_input)

        # final validations
        if var_name == "":
            return False, "Empty var name: [%s]" % str_input

        if var_value == "":
            return False, "Empty var value: [%s]" % str_input

        # add new variable to internal data
        self.data.append( (var_name, var_value, parsed_opts) )

        return True, None

    def parse_variable_options(self, str_input):

        local_str_input = str_input.strip()

        opt_name = None
        opt_val = None
        parsed_opts = []

        counter = -1
        while True:
            counter += 1

            if counter >= self.max_number_options:
                return False, "Failed parsing: [%s]. Maximum number of options exceeded: [%s]." % (str_input, self.max_number_options), None

            v, r1, r2, r3 = self.parse_next_option(local_str_input)
            if not v:
                return False, "Failed parsing variable options: [%s]" % r1, None
            parsed_opts.append(r1)
            local_str_input = r2
            if not r3: # there are no more options
                break

        v, r = miniparse.scan_and_slice_beginning(local_str_input, self.ANYSPACE + self.EQ_SIGN)
        if not v:
            return False, "Failed parsing: [%s]. Unpexteced sequence found before equal sign." % str_input, None

        return True, parsed_opts, local_str_input

    def parse_next_option(self, str_input):

        opt_name = None
        opt_val = None

        more_options = None

        local_str_input = str_input.strip()
        if local_str_input == "":
            return False, "Invalid option input: [%s]" % str_input, None, None

        # start by parsing the option's name
        v, r = miniparse.scan_and_slice_beginning(local_str_input, self.VAR_ID + self.ANYSPACE + self.COLON)
        if v:

            # option has value

            opt_name = (r[0]).strip()
            local_str_input = (r[1]).strip()

            # remove the colon off the option's name
            v, r = miniparse.remove_last_of(opt_name, self.COLON)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            opt_name = r.strip()

            # find next quote (option's value - first)
            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.QUOTE)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            local_str_input = r[1]

            # forward until closing quote is found (the next not escaped)
            v, r = miniparse.next_not_escaped_slice(local_str_input, "\"", self.BSLASH)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            opt_val = r[0]
            local_str_input = (r[1]).strip()

            # find next quote (option's value - second)
            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.QUOTE)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            local_str_input = (r[1]).strip()

            # descape the value, and its ready for storage
            v, r = miniparse.descape(opt_val, self.BSLASH)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            opt_val = r

            # expand the option's value
            v, r = self._expand(opt_val)
            if not v:
                return False, "Variable expansion failed: [%s]" % opt_val, None, None
            opt_val = r

            # need to advance past this option to look ahead for the next
            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.FSLASH)
            more_options = v

            if more_options:
                local_str_input = (r[1]).strip()
            if not more_options:

                # there are no other options

                v, r = miniparse.scan_and_slice_beginning(local_str_input, self.RCBRACKET)
                if not v:
                    return False, "Parsing option failed: [%s]" % str_input, None, None
                local_str_input = (r[1]).strip()

        else:

            # option has no value

            rem_last_chr = self.FSLASH
            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.VAR_ID + self.ANYSPACE + self.FSLASH)
            more_options = v
            if not more_options:

                # there are no other options

                v, r = miniparse.scan_and_slice_beginning(local_str_input, self.VAR_ID + self.ANYSPACE + self.RCBRACKET)
                if not v:
                    return False, "Parsing option failed: [%s]" % str_input, None, None
                local_str_input = (r[1]).strip()
                rem_last_chr = self.RCBRACKET

            else:
                local_str_input = (r[1]).strip()

            opt_name = (r[0]).strip()
            v, r = miniparse.remove_last_of(opt_name, rem_last_chr)
            if not v:
                return False, "Parsing option failed: [%s]" % str_input, None, None
            opt_name = r.strip()

        if more_options:
            # there are more options. signal for continuation
            return True, (opt_name, opt_val), local_str_input, True
        else:
            # there are no more options. signal for termination
            return True, (opt_name, opt_val), local_str_input, False

        return False, "Failed parsing options: [%s]" % str_input, None, None

    def getallvars(self):
        return self.data

    def getvars(self, varname):
        ret = []
        for v in self.data:
            if v[0] == varname:
                ret.append(v)
        return ret
