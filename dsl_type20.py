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
# lines starting with "#" are skipped (treated as comment)
# the comment character may come anywhere in the line
# lines are string-trimmed (extra spaces are removed)
# variable names and options can be repeated
# variables can be grouped in "contexts", syntax is as follows:
#
# [
# @context-name
# var1 = "val1"
# ]
#

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

def printable_context(context):
    if context is None:
        return "(global context)"
    return context

def select_dsltype20_options(expand_envvars = False, expand_user = False):
    opts = DSLType20_Options()
    opts._expand_envvars = expand_envvars
    opts._expand_user = expand_user
    return opts

class DSLType20_Options:
    def __init__(self):
        self._expand_envvars = False
        self._expand_user = False

class DSLType20:
    def __init__(self, _options):

        # internal
        self.data = {}
        self.global_context_id = "global context" # unparseable string - so as to not impose too many restrictions on client code
        self.max_number_variable_options = 1024
        self.clear()

        # string parsing
        self.IDENTIFIER = "[_\\-a-zA-Z0-9]+"
        self.ANYSPACE = "[ ]*"
        self.COLON = ":"
        self.AT_SIGN = "@"
        self.LBRACKET = "["
        self.RBRACKET = "]"
        self.LCBRACKET = "{"
        self.RCBRACKET = "}"
        self.EQ_SIGN = "="
        self.QUOTE = "\""
        self.BSLASH = "\\"
        self.FSLASH = "/"

        # read options
        self.expand_envvars = _options._expand_envvars
        self.expand_user = _options._expand_user

    def clear(self):
        self.data = {}
        self.data[self.global_context_id] = []

    def _expand(self, str_input):

        if str_input is None:
            return False, str_input

        if not isinstance(str_input, str):
            return False, str_input

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

    def add_context(self, context):

        if not isinstance(context, str):
            return False

        v, r = miniparse.scan_and_slice_beginning(context, self.IDENTIFIER)
        if not v:
            return False
        if r[1] != "":
            return False

        if context in self.data:
            return False

        self.data[context] = []
        return True

    def parse(self, contents):

        self.clear()

        context = None # global context
        expecting_context_name = False
        expecting_context_closure = False

        lines = contents.split("\n")
        for line in lines:

            line_t = self.sanitize_line(line)
            if line_t == "":
                continue

            if line_t == self.LBRACKET:
                if expecting_context_name or context is not None:
                    return False, "Failed parsing contents: nested contexts are not alllowed."
                expecting_context_name = True
                expecting_context_closure = True
                continue

            if line_t == self.RBRACKET:
                if expecting_context_name:
                    return False, "Last context name not specified."
                context = None
                expecting_context_closure = False
                continue

            if expecting_context_name:
                expecting_context_name = False

                v, r = self._parse_context_name(line_t)
                if not v:
                    return v, r
                context = r
                self.add_context(context)
                continue

            v, r = self._parse_variable(line_t, context)
            if not v:
                return v, r

        if expecting_context_closure:
            return False, "Last context: [%s] was not closed." % printable_context(context)

        return True, None

    def _parse_context_name(self, str_input):

        local_str_input = str_input.strip()
        parsed_context_name = None
        remainder = None

        v, r = miniparse.scan_and_slice_beginning(local_str_input, self.AT_SIGN + self.ANYSPACE + self.IDENTIFIER)
        if not v:
            return False, "Malformed context name: [%s]." % str_input
        parsed_context_name = (r[0]).strip()
        remainder = (r[1]).strip()

        if not remainder == "":
            return False, "Malformed context name: [%s]." % str_input

        # remove the at ("@") sign
        v, r = miniparse.remove_next_of(parsed_context_name, self.AT_SIGN)
        if not v:
            return False, "Malformed context name: [%s]." % parsed_context_name
        parsed_context_name = r.strip()

        return True, parsed_context_name

    def _parse_variable(self, str_input, context=None):

        var_name = None
        var_value = None
        var_options = None
        parsed_opts = []

        local_str_input = str_input.strip()

        local_context = self.global_context_id
        if context is not None:
            local_context = context
        if not local_context in self.data:
            return False, "Can't parse variable: [%s]: Context doesn't exist: [%s]." % (str_input, context)

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

        # remove first quote of value
        v, r = miniparse.scan_and_slice_end(local_str_input, self.QUOTE)
        if not v:
            return False, "Malformed variable: [%s]: value must be be enclosed with quotes." % str_input
        local_str_input = (r[1]).strip()

        # remove equal sign just before the variable's value
        v, r = miniparse.scan_and_slice_end(local_str_input, self.EQ_SIGN)
        if not v:
            return False, "Malformed variable: [%s]: Failed to parse the equal sign before the variable's value." % str_input
        local_str_input = (r[1]).strip()

        v, r = miniparse.scan_and_slice_beginning(local_str_input, self.IDENTIFIER + self.ANYSPACE + self.LCBRACKET)
        if v:

            # variable has options

            var_name = r[0].strip()
            local_str_input = r[1].strip()

            v, r = miniparse.remove_last_of(var_name, self.LCBRACKET)
            if not v:
                return False, "Malformed variable: [%s]: Failed removing left bracket from options." % str_input
            var_name = r.strip()

            # parse the options
            v, r1, r2 = self._parse_variable_options(local_str_input)
            if not v:
                return False, "Failed parsing options: [%s]: [%s]" % (var_options, r1)
            parsed_opts = r1
            local_str_input = r2

            if len(local_str_input) != 0:
                return False, "Malformed variable: [%s]: Remaining unparseable contents: [%s]." % (str_input, local_str_input)

        else:

            # variable has no options

            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.IDENTIFIER + self.ANYSPACE)
            if not v:
                return False, "Malformed variable: [%s]: Can't parse variable name." % str_input
            var_name = (r[0]).strip()
            local_str_input = (r[1]).strip()

            if len(local_str_input) != 0:
                return False, "Malformed variable: [%s]: Remaining unparseable contents: [%s]." % (str_input, local_str_input)

        # final validations
        if var_name == "":
            return False, "Empty var name: [%s]" % str_input

        if var_value == "":
            return False, "Empty var value: [%s]" % str_input

        self.add_var(var_name, var_value, parsed_opts, local_context)

        return True, None

    def _parse_variable_options(self, str_input):

        local_str_input = str_input.strip()

        opt_name = None
        opt_val = None
        parsed_opts = []

        counter = -1
        while True:
            counter += 1

            if counter >= self.max_number_variable_options:
                return False, "Failed parsing: [%s]. Maximum number of options exceeded: [%s]." % (str_input, self.max_number_variable_options), None

            v, r1, r2, r3 = self._parse_next_option(local_str_input)
            if not v:
                return False, "Failed parsing variable options: [%s]" % r1, None
            parsed_opts.append(r1)
            local_str_input = r2
            if not r3: # there are no more options
                break

        return True, parsed_opts, local_str_input

    def _parse_next_option(self, str_input):

        opt_name = None
        opt_val = None

        more_options = None

        local_str_input = str_input.strip()
        if local_str_input == "":
            return False, "Invalid option input: [%s]" % str_input, None, None

        # start by parsing the option's name
        v, r = miniparse.scan_and_slice_beginning(local_str_input, self.IDENTIFIER + self.ANYSPACE + self.COLON)
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
            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.IDENTIFIER + self.ANYSPACE + self.FSLASH)
            more_options = v
            if not more_options:

                # there are no other options

                v, r = miniparse.scan_and_slice_beginning(local_str_input, self.IDENTIFIER + self.ANYSPACE + self.RCBRACKET)
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

    def get_all_vars(self, context=None):

        local_context = self.global_context_id
        if context is not None:
            local_context = context
        if not local_context in self.data:
            return None

        return self.data[local_context]

    def get_vars(self, varname, context=None):

        local_context = self.global_context_id
        if context is not None:
            local_context = context
        if not local_context in self.data:
            return None

        ret = []
        for v in self.data[local_context]:
            if v[0] == varname:
                ret.append(v)
        return ret

    def add_var(self, var_name, var_val, var_opts, context=None):

        local_context = context

        if local_context is None:
            local_context = self.global_context_id
        else:
            self.add_context(local_context)

        # validate var_name
        if not isinstance(var_name, str):
            return False
        v, r = miniparse.scan_and_slice_beginning(var_name, self.IDENTIFIER)
        if not v:
            return False
        if r[1] != "":
            return False

        # validate var_val
        if not isinstance(var_val, str):
            return False

        # validate var_opts
        if not isinstance(var_opts, list):
            return False
        for i in var_opts:
            if not isinstance(i, tuple):
                return False
            if not len(i) == 2:
                return  False
            if not isinstance(i[0], str):
                return False
            if not ( (isinstance(i[1], str)) or (i[1] is None) ):
                return False

        # expand the variable's value
        v, r = self._expand(var_val)
        if not v:
            return False, "Variable expansion failed: [%s]" % var_val
        var_val = r

        # expand the option's value
        var_opts_pre = var_opts
        var_opts = []
        for o in var_opts_pre:

            if o[1] is None:
                var_opts.append( o )
                continue

            v, r = self._expand(o[1])
            if not v:
                return False, "Option expansion failed: [%s]" % o[1]
            var_opts.append( (o[0], r) )

        # add new variable to internal data
        self.data[local_context].append( (var_name, var_val, var_opts) )

        return True

def puaq():
    print("Usage: %s file_to_parse.cfg" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        puaq()
    file_to_parse = sys.argv[1]

    dsl = DSLType20(False, False)

    if not os.path.exists(file_to_parse):
        print("File [%s] does not exist." % file_to_parse)
        sys.exit(1)

    file_contents = None
    with open(file_to_parse) as f:
        file_contents = f.read()

    v, r = dsl.parse(file_contents)
    if not v:
        print(r)
        sys.exit(1)
    print("File [%s] is parseable." % file_to_parse)
