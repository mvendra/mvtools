#!/usr/bin/env python3

import sys
import os

import path_utils
import miniparse

# class for parsing "dsl type 20"
# it is supposed to be a Create, Read and Delete - but not Update. (CRD, as in CRUD but without the U)
# updates are supposed to be done manually using text editors - to simplify the implementation.
#
# samples:
# variable1 = "value1" # quotes are mandatory for values
# variable1 = "value \"1\"" # quotes inside values must be escaped with "\"
# variable1 = "value \\2" # the escape character "\" itself has to be escaped
# variable2 {option1} = "value2"
# variable3 {option2 / option3: "value3"} = "value4"
# variable4 {option4: "value \"3\""} = "value \"5\"" # again, escaping quotes is necessary wherever you have a value
# newlines inside variable/option values are forbidden
#
# variables can be optionally decorated arbitrarily, by using the variable_decorator option during the DSL object construction
# example of a decorated variable (where variable_decorator = "* "):
# * variable1 = "value1"
#
# lines starting with "#" or "//" are skipped (treated as comment)
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
# contexts can have options too - when variables that belong to such contexts are
# requested, if vars_auto_ctx_options is set, then they are returned with the context's options
# in addition to their own:
#
# [
# @context-name {option1 / option2: "value1"}
# var2 = "val3"
# ]
#
# if allow_dupes is not set, then variable options take precedence over context options
# freestanding variables (defined outside any explicit contexts) belong to the "default context"

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
        return "(default context)"
    return context

def count_occurrence_first_of_pair(list_target, first_value):
    c = 0
    for i in list_target:
        if i[0] == first_value:
            c += 1
    return c

class DSLType20_Options:
    def __init__(self, expand_envvars = False, expand_user = False, allow_dupes = True, vars_auto_ctx_options=False, variable_decorator = ""):
        self._expand_envvars = expand_envvars
        self._expand_user = expand_user
        self._allow_dupes = allow_dupes
        self._vars_auto_ctx_options = vars_auto_ctx_options
        self._variable_decorator = variable_decorator

class DSLType20:
    def __init__(self, _options):

        # internal
        self.data = {}
        self.default_context_id = "default context" # unparseable string - so as to not impose too many restrictions on client code
        self.max_number_options = 1024
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
        self.NEWLINE = "\n"
        self.BSLASH = "\\"
        self.FSLASH = "/"
        self.COMMENTS = ["#"]

        # read options
        self.expand_envvars = _options._expand_envvars
        self.expand_user = _options._expand_user
        self.allow_dupes = _options._allow_dupes
        self.vars_auto_ctx_options = _options._vars_auto_ctx_options
        self.variable_decorator = _options._variable_decorator

    def clear(self):
        self.data = {}
        self.data[self.default_context_id] = [[], []]

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
        if line_out == "":
            return ""

        for c in self.COMMENTS:
            n = line_out.find(c)
            if n != -1:
                line_out = line_out[:n]

        return line_out.strip()

    def produce(self):

        result = ""
        for ctx in self.data:
            result += self._produce_context(ctx)
        return result.strip()

    def _produce_context(self, context):

        if context is None:
            return None
        if context not in self.data:
            return None

        result = ""
        if context != self.default_context_id:
            result = ("\n[\n@" + context + (" %s" % (self._produce_options(self.data[context][0])) )).rstrip()

        for y in self.data[context][1]:

            cur_var = "\n" + self.variable_decorator + y[0] # variable's name

            # produce the options
            prod_opts = self._produce_options(y[2])
            if len(prod_opts) > 0:
                cur_var = ("%s %s" %  (cur_var, prod_opts))

            # add the variable's value
            v, r = miniparse.escape(y[1], self.BSLASH, [self.QUOTE])
            if not v:
                return None
            var_escaped_value = r

            cur_var += " = " + self.QUOTE + var_escaped_value + self.QUOTE

            result += cur_var

        if context != self.default_context_id:
            result += "\n]\n"

        return result

    def _produce_options(self, input_options):

        options_result = ""
        for o in range(len(input_options)):

            if o == 0: # first option
                options_result += "{"

            options_result += input_options[o][0] # option's name
            if input_options[o][1] is not None:
                # option has value
                v, r = miniparse.escape((input_options[o][1]), self.BSLASH, [self.QUOTE])
                if not v:
                    return None
                opt_escaped_value = r
                options_result += ": " + self.QUOTE + opt_escaped_value + self.QUOTE

            if o == (len(input_options)-1): # last option
                options_result += "}"
            else:
                options_result += " / "
        return options_result

    def add_context(self, context, context_options):

        if not isinstance(context, str):
            return False, "Invalid parameter"

        if not isinstance(context_options, list):
            return False, "Invalid parameter"

        v, r = miniparse.scan_and_slice_beginning(context, self.IDENTIFIER)
        if not v:
            return False, "Unable to parse context name: [%s]" % context
        if r[1] != "":
            return False, "Unable to parse context name: [%s]. Unexpected extra characters: [%s]" % (context, r[1])

        expanded_context_options = []
        for co in context_options:

            if co[1] is None:
                expanded_context_options.append( co )
                continue

            if self.NEWLINE in co[1]:
                return False, "Unable to parse context name: [%s]. Newlines are forbidden inside option values." % (context)

            v, r = self._expand(co[1])
            if not v:
                return False, "unable to expand context's option value: [%s : %s]" % (co[0], co[1])
            expanded_context_options.append( (co[0], r) )

        if context in self.data:
            return False, "Failed adding new context: [%s] already exists" % context

        self.data[context] = [expanded_context_options, []]
        return True, None

    def parse(self, contents):

        self.clear()

        context = None # default context
        context_options = []
        expecting_context_name = False
        expecting_context_closure = False

        lines = contents.split("\n")
        for line in lines:

            line_t = self.sanitize_line(line)
            if line_t == "":
                continue

            # context name, begin
            if line_t == self.LBRACKET:
                if expecting_context_name or context is not None:
                    return False, "Failed parsing contents: nested contexts are not alllowed."
                expecting_context_name = True
                expecting_context_closure = True
                continue

            # context name, end
            if line_t == self.RBRACKET:
                if expecting_context_name:
                    return False, "Last context name not specified."
                context = None
                expecting_context_closure = False
                continue

            # context name, the name itself
            if expecting_context_name:
                expecting_context_name = False

                v, r = self._parse_context_name(line_t)
                if not v:
                    return v, r
                context, context_options = r
                v, r = self.add_context(context, context_options)
                if not v:
                    return False, "Failed creating new context: [%s]." % r
                continue

            # freestanding (default context) variable
            v, r = self._parse_variable(line_t, context)
            if not v:
                return False, r

        if expecting_context_closure:
            return False, "Last context: [%s] was not closed." % printable_context(context)

        return True, None

    def _parse_context_name(self, str_input):

        local_str_input = str_input.strip()
        parsed_context_name = None
        parsed_opts = []

        v, r = miniparse.scan_and_slice_beginning(local_str_input, self.AT_SIGN + self.ANYSPACE + self.IDENTIFIER)
        if not v:
            return False, "Malformed context name: [%s]." % str_input
        parsed_context_name = (r[0]).strip()
        local_str_input = (r[1]).strip()

        if not local_str_input == "": # there might be options

            v, r = miniparse.scan_and_slice_beginning(local_str_input, self.ANYSPACE + self.LCBRACKET)

            if v: # yes there are options

                local_str_input = (r[1]).strip()

                # parse the options
                v, r1, r2 = self._parse_options(local_str_input)
                if not v:
                    return False, "Failed parsing options: [%s]: [%s]" % (local_str_input, r1)
                parsed_opts = r1
                local_str_input = r2

                if len(local_str_input) != 0:
                    return False, "Malformed context name: [%s]: Remaining unparseable contents: [%s]." % (str_input, local_str_input)

            else: # no, its rubbish
                return False, "Malformed context name: [%s]." % str_input

        # remove the at ("@") sign
        v, r = miniparse.remove_next_of(parsed_context_name, self.AT_SIGN)
        if not v:
            return False, "Malformed context name: [%s]." % parsed_context_name
        parsed_context_name = r.strip()

        return True, (parsed_context_name, parsed_opts)

    def _parse_variable(self, str_input, context=None):

        var_name = None
        var_value = None
        parsed_opts = []

        local_str_input = str_input.strip()

        if self.variable_decorator != "":
            if local_str_input.find(self.variable_decorator) != 0:
                return False, "Can't parse variable: [%s]: Decorator [%s] not found." % (str_input, self.variable_decorator)
            local_str_input = (local_str_input[len(self.variable_decorator):]).strip()

        local_context = self.default_context_id
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
            v, r1, r2 = self._parse_options(local_str_input)
            if not v:
                return False, "Failed parsing options: [%s]: [%s]" % (local_str_input, r1)
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

        v, r = self.add_var(var_name, var_value, parsed_opts, local_context)
        if not v:
            return False, "Unable to add variable [%s]: [%s]" % (var_name, r)

        return True, None

    def _parse_options(self, str_input):

        local_str_input = str_input.strip()

        opt_name = None
        opt_val = None
        parsed_opts = []

        counter = -1
        while True:
            counter += 1

            if counter >= self.max_number_options:
                return False, "Failed parsing: [%s]. Maximum number of options exceeded: [%s]." % (str_input, self.max_number_options), None

            v, r1, r2, r3 = self._parse_next_option(local_str_input)
            if not v:
                return False, "Failed parsing options: [%s]" % r1, None
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
            v, r = miniparse.next_not_escaped_slice(local_str_input, self.QUOTE, self.BSLASH)
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
        return self.get_vars(None, context)

    def get_all_contexts(self):

        result = []
        for k in self.data:
            if k != self.default_context_id:
                result.append(k)
        return result

    def get_context_options(self, context):

        if context is None or context == "" or not isinstance(context, str):
            return False, "Context [%s] is invalid." % context

        if not context in self.data:
            return False, "Context [%s] does not exist." % context

        return self.data[context][0]

    def get_vars(self, varname, context=None):

        local_context = self.default_context_id
        if context is not None:
            local_context = context
        if not local_context in self.data:
            return None

        ret = []
        ctx_options_to_add = []
        for v in self.data[local_context][1]:
            if ((varname is not None) and (v[0] == varname)) or (varname is None):

                # add context options to the return list, if the option is enabled
                if self.vars_auto_ctx_options:
                    if not self.allow_dupes: # variable options will override context options
                        for co in self.data[local_context][0]:
                            if count_occurrence_first_of_pair(v[2], co[0]) < 1:
                                # var option and context option dupe. skip this context option - i.e. the var's option will effectively override this ctx opt
                                ctx_options_to_add.append(co)
                    else:
                        ctx_options_to_add = self.data[local_context][0]

                ret.append( (v[0], v[1], ctx_options_to_add + v[2] ) )

        return ret

    def add_var(self, var_name, var_val, var_opts, context=None):

        # validate var_name
        if not isinstance(var_name, str):
            return False, "variable's name is not a string"
        v, r = miniparse.scan_and_slice_beginning(var_name, self.IDENTIFIER)
        if not v:
            return False, "malformed variable"
        if r[1] != "":
            return False, "malformed varialbe (invalid leftovers)"

        # validate var_val
        if not isinstance(var_val, str):
            return False, "variable's value is not a string"
        if var_val is not None:
            if self.NEWLINE in var_val:
                return False, "newlines are forbidden inside values"

        # validate var_opts
        if not isinstance(var_opts, list):
            return False, "variable's options are not a list"
        for i in var_opts:
            if not isinstance(i, tuple):
                return False, "variable's options are not tuples in a list"
            if not len(i) == 2:
                return  False, "variable's options are not pair of tuples in a list"
            if not isinstance(i[0], str):
                return False, "variable's options's identifier is not a string"
            if not ( (isinstance(i[1], str)) or (i[1] is None) ):
                return False, "variable's options's value is invalid"
            if i[1] is not None:
                if self.NEWLINE in i[1]:
                    return False, "newlines are forbidden inside values"

        # expand the variable's value
        v, r = self._expand(var_val)
        if not v:
            return False, "unable to expand variable's value: [%s]" % var_val
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
                return False, "unable to expand variable's option value: [%s : %s]" % (o[0], o[1])
            var_opts.append( (o[0], r) )

        local_context = context
        if local_context is None:
            local_context = self.default_context_id
        else:
            self.add_context(local_context, [])

        # check for duplicates, if checking is enabled
        if not self.allow_dupes:

            # check for duplicated variable
            for v in self.data[local_context][1]:
                if v[0] == var_name:
                    return False, "variable [%s] is duplicated" % v[0]

            # check for duplicated option inside the provided options
            for o in var_opts:
                if count_occurrence_first_of_pair(var_opts, o[0]) > 1:
                    return False, "option [%s] is duplicated" % o[0]

        # add new variable to internal data
        self.data[local_context][1].append( (var_name, var_val, var_opts) )

        return True, None

    def rem_var(self, var_name, index=None, context=None):

        local_context = self.default_context_id
        if context is not None:
            local_context = context
        if not local_context in self.data:
            return False

        local_all_vars_new = []
        local_all_vars = self.data[local_context][1]

        for i in range(len(local_all_vars)):

            if (local_all_vars[i])[0] == var_name:

                if index is not None:
                    if index == i:
                        continue
                else:
                    continue

            local_all_vars_new.append(local_all_vars[i])

        self.data[local_context][1] = local_all_vars_new

        return (len(local_all_vars) != len(local_all_vars_new))

    def rem_ctx(self, context):

        if context == self.default_context_id:
            return False
        if not isinstance(context, str):
            return False
        if not context in self.data:
            return False

        try:
            del self.data[context]
        except:
            return False

        return True

def puaq():
    print("Usage: %s file_to_parse.t20" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        puaq()
    file_to_parse = sys.argv[1]

    dsl = DSLType20(DSLType20_Options())

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
