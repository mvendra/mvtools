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
# variable1 # variable defined but no value set (i.e. value-less variable)
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

# string parsing
IDENTIFIER = "[_\\-a-zA-Z0-9]+"
ANYSPACE = "[ ]*"
SINGLESPACE = " "
COLON = ":"
ATSIGN = "@"
LBRACKET = "["
RBRACKET = "]"
LCBRACKET = "{"
RCBRACKET = "}"
EQSIGN = "="
QUOTE = "\""
NEWLINE = "\n"
BSLASH = "\\"
FSLASH = "/"
COMMENTS = ["#", "//"]

# basic types
DSLTYPE20_ENTRY_TYPE_VAR = 1
DSLTYPE20_ENTRY_TYPE_OPT = 2
DSLTYPE20_ENTRY_TYPE_CTX = 3

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

class DSLType20_Variable:
    def __init__(self, name, value, options):

        self.name = name
        self.value = value
        self.options = options

        # validate name
        if not isinstance(name, str):
            return False, "Variable's name is not a string"
        v, r = miniparse.scan_and_slice_beginning(name, IDENTIFIER)
        if not v:
            return False, "Malformed variable"
        if r[1] != "":
            return False, "Malformed varialbe (invalid leftovers)"

        # validate value
        if value is not None:
            if NEWLINE in value:
                return False, "Newlines are forbidden inside values"

        # expand the variable's value
        if value is not None:
            v, r = self._expand(value)
            if not v:
                return False, "Unable to expand variable's value: [%s]" % value
            value = r

    def get_type(self):
        return DSLTYPE20_ENTRY_TYPE_VAR

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_options(self):
        return self.options

class DSLType20_Option:
    def __init__(self, name, value):
        self.name = name
        self.value = value

        # validate and expand
        if self.value is not None:
            if NEWLINE in self.value:
                return False, "Newlines are forbidden inside values"
            v, r = self._expand(self.value)
            if not v:
                return False, "Unable to expand option's value: [%s : %s]" % (self.name, self.value)
            self.value = r

    def get_type(self):
        return DSLTYPE20_ENTRY_TYPE_OPT

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

class DSLType20_Context:
    def __init__(self, ptr_parent, name, options):
        self.ptr_parent = ptr_parent
        self.name = name
        self.options = options
        self.entries = []

    def get_type(self):
        return DSLTYPE20_ENTRY_TYPE_CTX

    def get_ptr_parent(self):
        return self.ptr_parent

    def get_name(self):
        return self.name

    def get_options(self):
        return self.options

    def get_entries(self):
        return self.entries

    def add_entry(self, new_entry):
        self.entries.append(new_entry)

class DSLType20_Config:
    def __init__(self, expand_envvars = False, expand_user = False, allow_dupes = True, vars_auto_ctx_options=False, variable_decorator = ""):
        self._expand_envvars = expand_envvars
        self._expand_user = expand_user
        self._allow_dupes = allow_dupes
        self._vars_auto_ctx_options = vars_auto_ctx_options
        self._variable_decorator = variable_decorator

class DSLType20:
    def __init__(self, _options):

        # internal
        self.data = None
        self.default_context_id = "default-context"
        self.max_number_options = 1024
        self.clear()

        # read options
        self.expand_envvars = _options._expand_envvars
        self.expand_user = _options._expand_user
        self.allow_dupes = _options._allow_dupes
        self.vars_auto_ctx_options = _options._vars_auto_ctx_options
        self.variable_decorator = _options._variable_decorator

    def clear(self):
        self.data = None
        self.data = DSLType20_Context(None, self.default_context_id, [])

    def add_context(self, parent_context, context_name, context_options):

        # context_options: expected as a list of tuples ("neutral" format)

        if parent_context is None:
            parent_context = self.default_context_id

        # precond validations # mvtodo: not here
        if not isinstance(context_name, str):
            return False, "Invalid parameter (context_name): [%s]" % context_name

        # validate context name # mvtodo: also not here
        v, r = miniparse.scan_and_slice_beginning(context_name, IDENTIFIER)
        if not v:
            return False, "Unable to parse context name: [%s]" % context_name
        if r[1] != "":
            return False, "Unable to parse context name: [%s]. Unexpected extra characters: [%s]" % (context_name, r[1])

        # convert incoming options from "neutral" format into options objects list
        v, r = self._make_obj_opt_list(context_options)
        if not v:
            return False, v
        opts_obj_list = r

        # first check if the context doesn't already exist
        if self._find_context(context_name, None, None):
            return False, "Failed adding new context: [%s] already exists" % context_name

        # add new context to the internal datastructure
        if not self._find_context(parent_context, self._add_ctx_helper, (context_name, opts_obj_list)):
            return False, "Unable to add context [%s] to [%s] - the latter cannot be found." % (context_name, parent_context)

        return True, None

    def get_sub_contexts(self, parent_context):

        if parent_context is None:
            parent_context = self.default_context_id

        result = []

        if not self._find_context(parent_context, self._get_sub_contexts_helper, result):
            return False, "Unable to return sub contexts of [%s] - context not found." % parent_context

        return result

    def get_context_options(self, context):

        result = []

        if context is None:
            context = self.default_context_id

        if not self._find_context(context, self._get_context_opts_helper, result):
            return False, "Context [%s] does not exist." % context

        return result

    def rem_context(self, context):

        ctx_info = []

        if context is None or context == self.default_context_id:
            return False, "Removing the default context is forbidden"

        if not self._find_context(context, self._rem_context_helper, ctx_info):
            return False, "Context [%s] does not exist." % context

        if len(ctx_info) != 1:
            return False, "Found more than one instance of context [%s]. Fatal error." % context

        ctx_parent = ctx_info[0].get_ptr_parent()
        if ctx_parent is None:
            return False, "Context [%s] has no parent." % context

        idx = 0
        entry_found = False
        for ctx in ctx_parent.get_entries():
            if ctx.get_name() == context:
                entry_found = True
                break
            idx += 1

        if not entry_found:
            return False, "Context [%s] could not be removed (not found under its parent)" % context

        try:
            del ctx_parent.get_entries()[idx]
        except:
            return False, "Context [%s] could not be removed (unknown reason)" % context

        return True, None

    def add_variable(self, var_name, var_val, var_opts, context=None):

        # convert incoming options from "neutral" format into options objects list
        v, r = self._make_obj_opt_list(var_opts)
        if not v:
            return False, v
        opts_obj_list = r

        # add context to the default context if it does not preexist
        if context is None:
            context = self.default_context_id
        else:
            self.add_context(None, context, []) # mvtodo: wrong

        # add new variable to internal data
        if not self._find_context(context, self._add_variable_helper, (var_name, var_val, opts_obj_list)):
            return False, "Context [%s] does not exist." % context
        return True, None

    def get_all_variables(self, context=None):
        return self.get_variables(None, context)

    def get_variables(self, varname, context=None):

        if context is None:
            context = self.default_context_id
        result = []

        # mvtodo: reimplement inheriting options from parent context -> @stashed-inherit-opts-from-ctx-vars

        if not self._find_context(context, self._get_variable_helper, result):
            return False, "Context [%s] does not exist." % context
        return True, result

    def rem_variable(self, var_name, context=None):

        if context is None:
            context = self.default_context_id
        result = []

        if not self._find_context(context, self._rem_variable_helper, (var_name, result)):
            return False, "Context [%s] does not exist." % context
        return True, result

    def parse(self, contents):

        self.clear()

        context = None # default context
        context_options = []
        expecting_context_name = False
        expecting_context_closure = False

        lines = contents.split(NEWLINE)
        for line in lines:

            line_t = self._sanitize_line(line)
            if line_t is None:
                return False, "Unable to sanitize line: [%s]" % line
            if line_t == "":
                continue

            # context name, begin
            if line_t == LBRACKET:
                if expecting_context_name or context is not None:
                    return False, "Failed parsing contents: nested contexts are not alllowed."
                expecting_context_name = True
                expecting_context_closure = True
                continue

            # context name, end
            if line_t == RBRACKET:
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
                v, r = self.add_context(context, context_options) # mvtodo: wrong
                if not v:
                    return False, "Failed creating new context: [%s]." % r
                continue

            # freestanding (default context) variable
            v, r = self._parse_variable(line_t, context)
            if not v:
                return False, r

        if expecting_context_closure:
            return False, "Last context: [%s] was not closed." % printable_context(context) # mvtodo: replace with ctx.get_name() and ditch printable_context

        return True, None

    def produce(self):

        result = ""
        result += self._produce_context(self.data)
        return result.strip()

    def _find_context(self, context_name, callback_func, callback_data):

        if context_name is None:
            context_name = self.default_context_id

        ptr_match = None
        ctx_to_nav = []
        ctx_to_nav.append(self.data)

        while (len(ctx_to_nav) > 0):

            current = ctx_to_nav.pop()

            if current.get_type() == DSLTYPE20_ENTRY_TYPE_VAR:
                continue

            if current.get_name() == context_name:
                ptr_match = current
                break

            for entry in current.get_entries():
                if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                    ctx_to_nav.append(entry)

        if ptr_match is not None and callback_func is not None:
            callback_func(ptr_match, callback_data)

        return (ptr_match is not None)

    def _add_ctx_helper(self, ptr, cb_data_ctx):

        new_ctx = DSLType20_Context(ptr, cb_data_ctx[0], cb_data_ctx[1])
        ptr.add_entry(new_ctx)

    def _get_sub_contexts_helper(self, ptr, cb_data_res):

        for entry in ptr.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                cb_data_res.append(entry)

    def _get_context_opts_helper(self, ptr, cb_data_res):

        cb_data_res += ptr.get_options()

    def _rem_context_helper(self, ptr, cb_data_rem):

        cb_data_rem.append(ptr)

    def _add_variable_helper(self, ptr, cb_data_add):

        # mvtodo: check for dupes if enabled {if not self.allow_dupes:} -> @stashed-sample

        var_name, var_val, var_opts = cb_data_add
        new_var = DSLType20_Variable(var_name, var_val, var_opts)
        ptr.add_entry(new_var)

    def _get_variable_helper(self, ptr, cb_data_get):

        # mvtodo: check for dupes if enabled {if not self.allow_dupes:} -> @stashed-sample

        for entry in ptr.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR:
                cb_data_get.append(entry)

    def _rem_variable_helper(self, ptr, cb_data_rem):

        var_name, result = cb_data_rem
        new_entries_list = []
        entries_ptr = ptr.get_entries()

        for entry in entries_ptr:
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR and entry.get_name() == var_name:
                result.append(entry.get_name()) # this is just to make it easy to tell how many entries were skipped (deleted)
            else:
                new_entries_list.append(entry)

        entries_ptr.clear()
        entries_ptr = new_entries_list

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

    def _sanitize_line(self, line_in):

        line_out = line_in.strip()
        if line_out == "":
            return ""

        for c in COMMENTS:
            line_out = miniparse.guarded_right_cut(line_out, list(c), QUOTE)
            if line_out is None:
                return None
            if line_out == "":
                return ""

        return line_out.strip()

    def _make_obj_opt_list(self, options):

        result = []

        # validate options
        if not isinstance(options, list):
            return False, "Options are not a list"
        for i in options:
            if not isinstance(i, tuple):
                return False, "Options are not tuples in a list"
            if not len(i) == 2:
                return  False, "Options are not pair of tuples in a list"
            if not isinstance(i[0], str):
                return False, "Options's identifier is not a string"
            if not ( (isinstance(i[1], str)) or (i[1] is None) ):
                return False, "Options's value is invalid"

        for opt in options:
            opt_name, opt_val = opt
            opt_obj = DSLType20_Option(opt_name, opt_val)
            result.append(opt_obj)

        return True, result

    def _produce_context(self, context):

        if context is None:
            return None
        if context not in self.data:
            return None

        result = ""
        if context != self.default_context_id:
            result = (NEWLINE + LBRACKET + NEWLINE + ATSIGN + context + (" %s" % (self._produce_options(self.data[context][0])) )).rstrip()

        for y in self.data[context][1]:

            cur_var = NEWLINE + self.variable_decorator + y[0] # variable's name

            # produce the options
            prod_opts = self._produce_options(y[2])
            if len(prod_opts) > 0:
                cur_var = ("%s %s" %  (cur_var, prod_opts))

            # add the variable's value - if it has it
            if y[1] is not None:
                var_escaped_value = ""
                if y[1] != "":
                    v, r = miniparse.escape(y[1], BSLASH, [QUOTE])
                    if not v:
                        return None
                    var_escaped_value = r

                cur_var += SINGLESPACE + EQSIGN + SINGLESPACE + QUOTE + var_escaped_value + QUOTE

            result += cur_var

        if context != self.default_context_id:
            result += NEWLINE + RBRACKET + NEWLINE

        return result

    def _produce_options(self, input_options):

        options_result = ""
        for o in range(len(input_options)):

            if o == 0: # first option
                options_result += LCBRACKET

            options_result += input_options[o][0] # option's name
            if input_options[o][1] is not None:
                # option has value
                opt_escaped_value = ""
                if input_options[o][1] != "":
                    v, r = miniparse.escape((input_options[o][1]), BSLASH, [QUOTE])
                    if not v:
                        return None
                    opt_escaped_value = r
                options_result += COLON + SINGLESPACE + QUOTE + opt_escaped_value + QUOTE

            if o == (len(input_options)-1): # last option
                options_result += RCBRACKET
            else:
                options_result += SINGLESPACE + FSLASH + SINGLESPACE

        return options_result

    def _parse_context_name(self, str_input):

        local_str_input = str_input.strip()
        parsed_context_name = None
        parsed_opts = []

        v, r = miniparse.scan_and_slice_beginning(local_str_input, ATSIGN + ANYSPACE + IDENTIFIER)
        if not v:
            return False, "Malformed context name: [%s]." % str_input
        parsed_context_name = (r[0]).strip()
        local_str_input = (r[1]).strip()

        if not local_str_input == "": # there might be options

            v, r = miniparse.scan_and_slice_beginning(local_str_input, ANYSPACE + LCBRACKET)

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
        v, r = miniparse.remove_next_of(parsed_context_name, ATSIGN)
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

        # start by parsing the variable's value - if it has it
        v, r = miniparse.scan_and_slice_end(local_str_input, QUOTE)
        if v:
            if r[1][len(r[1])-1] == BSLASH: # variable value was indeed enclosed with quotes, but the last quote was escaped. error.
                return False, "Malformed variable: [%s]: value must be be enclosed with a nonescaped quote (failed at the second quote)." % str_input
            local_str_input = r[1]

            # find next nonescaped quote in reverse (beginning of the value)
            v, r = miniparse.last_not_escaped_slice(local_str_input, QUOTE, BSLASH)
            if not v:
                return False, "Malformed variable: [%s]: can't find first quote of the variable's value." % str_input
            local_str_input = (r[1]).strip()
            var_value = r[0]

            # descape the variable's value
            v, r = miniparse.descape(var_value, BSLASH)
            if not v:
                return False, "Variable descaping failed: [%s]" % var_value
            var_value = r

            # remove first quote of value
            v, r = miniparse.scan_and_slice_end(local_str_input, QUOTE)
            if not v:
                return False, "Malformed variable: [%s]: value must be be enclosed with quotes." % str_input
            local_str_input = (r[1]).strip()

            # remove equal sign just before the variable's value
            v, r = miniparse.scan_and_slice_end(local_str_input, EQSIGN)
            if not v:
                return False, "Malformed variable: [%s]: Failed to parse the equal sign before the variable's value." % str_input
            local_str_input = (r[1]).strip()

        v, r = miniparse.scan_and_slice_beginning(local_str_input, IDENTIFIER + ANYSPACE + LCBRACKET)
        if v:

            # variable has options

            var_name = r[0].strip()
            local_str_input = r[1].strip()

            v, r = miniparse.remove_last_of(var_name, LCBRACKET)
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

            v, r = miniparse.scan_and_slice_beginning(local_str_input, IDENTIFIER + ANYSPACE)
            if not v:
                return False, "Malformed variable: [%s]: Can't parse variable name." % str_input
            var_name = (r[0]).strip()
            local_str_input = (r[1]).strip()

            if len(local_str_input) != 0:
                return False, "Malformed variable: [%s]: Remaining unparseable contents: [%s]." % (str_input, local_str_input)

        # final validations
        if var_name == "":
            return False, "Empty var name: [%s]" % str_input

        v, r = self.add_variable(var_name, var_value, parsed_opts, local_context)
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
        v, r = miniparse.scan_and_slice_beginning(local_str_input, IDENTIFIER + ANYSPACE + COLON)
        if v:

            # option has value

            opt_name = (r[0]).strip()
            local_str_input = (r[1]).strip()

            # remove the colon off the option's name
            v, r = miniparse.remove_last_of(opt_name, COLON)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            opt_name = r.strip()

            # find next quote (option's value - first)
            v, r = miniparse.scan_and_slice_beginning(local_str_input, QUOTE)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            local_str_input = r[1]

            # forward until closing quote is found (the next not escaped)
            v, r = miniparse.next_not_escaped_slice(local_str_input, QUOTE, BSLASH)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            opt_val = r[0]
            local_str_input = (r[1]).strip()

            # find next quote (option's value - second)
            v, r = miniparse.scan_and_slice_beginning(local_str_input, QUOTE)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            local_str_input = (r[1]).strip()

            # descape the value, and its ready for storage
            v, r = miniparse.descape(opt_val, BSLASH)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            opt_val = r

            # need to advance past this option to look ahead for the next
            v, r = miniparse.scan_and_slice_beginning(local_str_input, FSLASH)
            more_options = v

            if more_options:
                local_str_input = (r[1]).strip()
            if not more_options:

                # there are no other options

                v, r = miniparse.scan_and_slice_beginning(local_str_input, RCBRACKET)
                if not v:
                    return False, "Parsing option failed: [%s]" % str_input, None, None
                local_str_input = (r[1]).strip()

        else:

            # option has no value

            rem_last_chr = FSLASH
            v, r = miniparse.scan_and_slice_beginning(local_str_input, IDENTIFIER + ANYSPACE + FSLASH)
            more_options = v
            if not more_options:

                # there are no other options

                v, r = miniparse.scan_and_slice_beginning(local_str_input, IDENTIFIER + ANYSPACE + RCBRACKET)
                if not v:
                    return False, "Parsing option failed: [%s]" % str_input, None, None
                local_str_input = (r[1]).strip()
                rem_last_chr = RCBRACKET

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

def puaq():
    print("Usage: %s file_to_parse.t20" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        puaq()
    file_to_parse = sys.argv[1]

    dsl = DSLType20(DSLType20_Config())

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
