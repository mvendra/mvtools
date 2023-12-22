#!/usr/bin/env python3

import sys
import os

import path_utils
import miniparse
import mvtools_exception

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
NULL = "\x00"
SPACE = " "
HTAB = "\t"
BSLASH = "\\"
FSLASH = "/"
COMMENTS = ["#", "//"]

# basic types
DSLTYPE20_ENTRY_TYPE_VAR = 1
DSLTYPE20_ENTRY_TYPE_OPT = 2
DSLTYPE20_ENTRY_TYPE_CTX = 3

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

def expand_value(configs, str_input):

    if str_input is None:
        return True, None

    if not isinstance(str_input, str):
        return False, str_input

    local_str_input = str_input

    if configs.expand_envvars:
        local_str_input = os.path.expandvars(local_str_input)
        if "$" in local_str_input:
            return False, str_input

    if configs.expand_user:
        local_str_input = os.path.expanduser(local_str_input)
        if "~" in local_str_input:
            return False, str_input

    return True, local_str_input

def sanitize_line(line_in):

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

def validate_name(name):

    if name is None:
        return False

    if not isinstance(name, str):
        return False

    if NEWLINE in name:
        return False

    if NULL in name:
        return False

    if SPACE in name:
        return False

    if HTAB in name:
        return False

    if not len(name) >= 1:
        return False

    return True

def validate_value(value):

    if value is None:
        return True

    if not isinstance(value, str):
        return False

    if NEWLINE in value:
        return False

    if NULL in value:
        return False

    return True

def validate_variable(name, value):

    # validate name
    if not validate_name(name):
        return False, "Variable name is invalid"

    # validate value
    if not validate_value(value):
        return False, "Variable value is invalid"

    return True, None

def validate_option(name, value):

    # validate name
    if not validate_name(name):
        return False, "Option name is invalid"

    # validate value
    if not validate_value(value):
        return False, "Option value is invalid"

    return True, None

def validate_options_list(options):

    if options is None:
        return False, "Options are None"

    if not isinstance(options, list):
        return False, "Options are not a list"

    opt_name_map = {}
    for opt in options:

        if not isinstance(opt, tuple):
            return False, "Options are not tuples in a list"

        if not len(opt) == 2:
            return False, "Options are not pair of tuples in a list"

        v, r = validate_option(opt[0], opt[1])
        if not v:
            return False, r

        if opt[0] in opt_name_map:
            return False, "Duplicated option: [%s]" % opt[0]
        opt_name_map[opt[0]] = True

    return True, None

def validate_context(context_name):

    # validate name
    if not validate_name(context_name):
        return False, "Context name is invalid"

    return True, None

def make_obj_opt_list(configs, options):

    result = []

    v, r = validate_options_list(options)
    if not v:
        return False, r

    for opt in options:
        opt_name, opt_val = opt
        opt_obj = DSLType20_Option(configs, opt_name, opt_val)
        result.append(opt_obj)

    return True, result

def opt_list_has(options, name):

    for opt in options:
        if opt.get_name() == name:
            return True, opt
    return False, None

def inherit_options(parent_options, new_options):

    result = []

    # first pass: try to add everything from parent, unless its also present in the new
    for p_opt in parent_options:
        v, r = opt_list_has(new_options, p_opt.get_name())
        if not v:
            result.append(p_opt)

    # second pass: add everything from new, except for doubletapped valueless options
    for n_opt in new_options:
        v, r = opt_list_has(parent_options, n_opt.get_name())
        if v: # common option - let's look further
            if r.get_value() is None and n_opt.get_value() is None:
                continue # doubletapped, valueless option. drop/skip
        result.append(n_opt)

    return result

class DSLType20_Variable:
    def __init__(self, configs, name, value, options):

        self.configs = configs
        self.name = name
        self.value = value
        self.options = options

        v, r = validate_variable(self.name, self.value)
        if not v:
            raise mvtools_exception.mvtools_exception(r)

        # expand the value
        v, r = expand_value(self.configs, self.value)
        if not v:
            raise mvtools_exception.mvtools_exception("Unable to expand variable's value: [%s : %s]" % (self.name, self.value))
        self.value = r

    def get_type(self):
        return DSLTYPE20_ENTRY_TYPE_VAR

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_options(self):
        return self.options

class DSLType20_Option:
    def __init__(self, configs, name, value):

        self.configs = configs
        self.name = name
        self.value = value

        v, r = validate_option(self.name, self.value)
        if not v:
            raise mvtools_exception.mvtools_exception(r)

        # expand the value
        v, r = expand_value(self.configs, self.value)
        if not v:
            raise mvtools_exception.mvtools_exception("Unable to expand option's value: [%s : %s]" % (self.name, self.value))
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

        v, r = validate_context(self.name)
        if not v:
            raise mvtools_exception.mvtools_exception(r)

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
    def __init__(self, expand_envvars = False, expand_user = False, allow_var_dupes = True, inherit_options = False, variable_decorator = ""):

        self.expand_envvars = expand_envvars
        self.expand_user = expand_user
        self.allow_var_dupes = allow_var_dupes
        self.inherit_options = inherit_options
        self.variable_decorator = variable_decorator

class DSLType20:
    def __init__(self, _configs):

        # internal
        self.data = None
        self.default_context_id = "default-context"
        self.max_number_options = 1024
        self.clear()

        # read configs
        self.configs = _configs

    def clear(self):
        self.data = None
        self.data = DSLType20_Context(None, self.default_context_id, [])

    def add_context(self, parent_ctx, ctx_name, ctx_options):

        # ctx_options: expected as a list of tuples ("neutral" format)

        if parent_ctx is None:
            parent_ctx = self.default_context_id

        # pre-validate context name
        v, r = validate_context(ctx_name)
        if not v:
            return False, r

        # pre-validate options
        v, r = validate_options_list(ctx_options)
        if not v:
            return False, r

        # convert incoming options from "neutral" format into options objects list
        v, r = make_obj_opt_list(self.configs, ctx_options)
        if not v:
            return False, r
        opts_obj_list = r

        # first check if the context doesn't already exist
        v, r = self._find_context(ctx_name, None, None)
        if not v:
            return False, r
        if r:
            return False, "Failed adding new context: [%s] already exists" % ctx_name

        # add new context to the internal datastructure
        v, r = self._find_context(parent_ctx, self._add_ctx_helper, (ctx_name, opts_obj_list))
        if not v:
            return False, r
        if not r:
            return False, "Unable to add context [%s] to [%s] - the latter cannot be found." % (ctx_name, parent_ctx)

        return True, None

    def get_context(self, context_name, parent_context = None):

        if context_name is None or context_name == self.default_context_id:
            return True, self.data

        if parent_context is None:
            parent_context = self.default_context_id

        result_ptr = []

        v, r = self._find_context(parent_context, self._get_context_helper, (context_name, result_ptr))
        if not v:
            return False, r
        if not r:
            return False, "Unable to return context [%s] of [%s] - context not found." % (context_name, parent_context)

        if len(result_ptr) == 0:
            result_ptr = None
        else:
            result_ptr = result_ptr[0]
        return True, result_ptr

    def get_sub_contexts(self, parent_context):

        if parent_context is None:
            parent_context = self.default_context_id

        result = []

        v, r = self._find_context(parent_context, self._get_sub_contexts_helper, result)
        if not v:
            return False, r
        if not r:
            return False, "Unable to return sub contexts of [%s] - context not found." % parent_context

        return True, result

    def get_context_options(self, context_name):

        result = []

        if context_name is None:
            context_name = self.default_context_id

        v, r = self._find_context(context_name, self._get_context_opts_helper, result)
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context_name

        return True, result

    def rem_context(self, context_name):

        ctx_info = []

        if context_name is None or context_name == self.default_context_id:
            return False, "Removing the default context is forbidden"

        v, r = self._find_context(context_name, self._rem_context_helper, ctx_info)
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context_name

        if len(ctx_info) != 1:
            return False, "Found more than one instance of context [%s]. Fatal error." % context_name

        ctx_parent = ctx_info[0].get_ptr_parent()
        if ctx_parent is None:
            return False, "Context [%s] has no parent." % context_name

        idx = 0
        entry_found = False
        for ctx in ctx_parent.get_entries():
            if ctx.get_name() == context_name:
                entry_found = True
                break
            idx += 1

        if not entry_found:
            return False, "Context [%s] could not be removed (not found under its parent)" % context_name

        try:
            del ctx_parent.get_entries()[idx]
        except:
            return False, "Context [%s] could not be removed (unknown reason)" % context_name

        return True, None

    def add_variable(self, var_name, var_val, var_opts, context = None):

        # pre-validate variable
        v, r = validate_variable(var_name, var_val)
        if not v:
            return False, r

        # pre-validate options
        v, r = validate_options_list(var_opts)
        if not v:
            return False, r

        # convert incoming options from "neutral" format into options objects list
        v, r = make_obj_opt_list(self.configs, var_opts)
        if not v:
            return False, r
        opts_obj_list = r

        # add context to the default context if it does not preexist
        if context is None:
            context = self.default_context_id
        else:
            self.add_context(None, context, [])

        # add new variable to internal data
        v, r = self._find_context(context, self._add_variable_helper, (var_name, var_val, opts_obj_list))
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context
        return True, None

    def get_all_variables(self, context = None):
        return self.get_variables(None, context)

    def get_variables(self, varname, context = None):

        if context is None:
            context = self.default_context_id
        result = []

        v, r = self._find_context(context, self._get_variable_helper, (varname, result))
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context
        return True, result

    def rem_all_variables(self, context = None):

        if context is None:
            context = self.default_context_id
        result = []

        v, r = self._find_context(context, self._rem_variable_helper, (None, result))
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context
        return True, result

    def rem_variable(self, var_name, context = None):

        if context is None:
            context = self.default_context_id
        result = []

        v, r = self._find_context(context, self._rem_variable_helper, (var_name, result))
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context
        return True, len(result)

    def parse(self, contents):

        self.clear()

        parent_context = None # default context
        context = None # default context
        context_options = []
        expecting_context_name = False
        expecting_context_closure = False

        lines = contents.split(NEWLINE)
        for line in lines:

            line_t = sanitize_line(line)
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
                v, r = self.add_context(parent_context, context, context_options)
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

    def _context_exists(self, ctx_name):

        v, r = self._find_context(ctx_name, None, None)
        return v

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
            v, r = callback_func(ptr_match, callback_data)
            if not v:
                return False, r

        return True, (ptr_match is not None)

    def _add_ctx_helper(self, ptr, cb_data_ctx):

        if self.configs.inherit_options:
            final_options = inherit_options(ptr.get_options(), cb_data_ctx[1])
        else:
            final_options = cb_data_ctx[1]

        new_ctx = DSLType20_Context(ptr, cb_data_ctx[0], final_options)
        ptr.add_entry(new_ctx)
        return True, None

    def _get_context_helper(self, ptr, cb_data_ctx):

        target_ctx_name, return_ptr = cb_data_ctx
        for entry in ptr.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX and entry.get_name() == target_ctx_name:
                return_ptr.append(entry)
                break
        return True, None

    def _get_sub_contexts_helper(self, ptr, cb_data_res):

        for entry in ptr.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                cb_data_res.append(entry)
        return True, None

    def _get_context_opts_helper(self, ptr, cb_data_res):

        cb_data_res += ptr.get_options()
        return True, None

    def _rem_context_helper(self, ptr, cb_data_rem):

        cb_data_rem.append(ptr)
        return True, None

    def _add_variable_helper(self, ptr, cb_data_add):

        var_name, var_val, var_opts = cb_data_add

        if not self.configs.allow_var_dupes:
            for entry in ptr.get_entries():
                if entry.get_name() == var_name:
                    return False, "Variable [%s] already exists" % var_name

        if self.configs.inherit_options:
            final_options = inherit_options(ptr.get_options(), var_opts)
        else:
            final_options = var_opts

        new_var = DSLType20_Variable(self.configs, var_name, var_val, final_options)
        ptr.add_entry(new_var)
        return True, None

    def _get_variable_helper(self, ptr, cb_data_get):

        var_name, list_ptr = cb_data_get

        for entry in ptr.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR and (entry.get_name() == var_name or var_name is None):
                list_ptr.append(entry)
        return True, None

    def _rem_variable_helper(self, ptr, cb_data_rem):

        var_name, result = cb_data_rem
        new_entries_list = []
        entries_ptr = ptr.get_entries()

        for entry in entries_ptr:
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR and (entry.get_name() == var_name or var_name is None):
                result.append(entry.get_name())
            else:
                new_entries_list.append(entry)

        entries_ptr.clear()
        for n in new_entries_list:
            entries_ptr.append(n)
        return True, None

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

    def _parse_variable(self, str_input, context = None):

        var_name = None
        var_value = None
        parsed_opts = []

        local_str_input = str_input.strip()

        if self.configs.variable_decorator != "":
            if local_str_input.find(self.configs.variable_decorator) != 0:
                return False, "Can't parse variable: [%s]: Decorator [%s] not found." % (str_input, self.configs.variable_decorator)
            local_str_input = (local_str_input[len(self.configs.variable_decorator):]).strip()

        local_context = self.default_context_id
        if context is not None:
            local_context = context
        if not self._context_exists(local_context):
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

    def _produce_context(self, context):

        if context is None:
            return None

        result = ""
        if context.get_name() != self.default_context_id:
            result = (NEWLINE + NEWLINE + LBRACKET + NEWLINE + ATSIGN + context.get_name() + (" %s" % ( self._produce_options(context.get_options()) ) )).rstrip()

        for entry in context.get_entries():

            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR:
                result += self._produce_variable(entry)

            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                result += self._produce_context(entry)

        if context.get_name() != self.default_context_id:
            result += NEWLINE + RBRACKET + NEWLINE

        return result

    def _produce_options(self, input_options):

        options_result = ""

        idx = 0
        for opt in input_options:
            idx += 1

            if idx == 1:
                options_result += LCBRACKET

            options_result += opt.get_name()

            if opt.get_value() is not None:
                # option has value
                opt_escaped_value = ""
                if opt.get_value() != "":
                    v, r = miniparse.escape(opt.get_value(), BSLASH, [QUOTE])
                    if not v:
                        return None
                    opt_escaped_value = r
                options_result += COLON + SINGLESPACE + QUOTE + opt_escaped_value + QUOTE

            if idx == len(input_options):
                options_result += RCBRACKET
            else:
                options_result += SINGLESPACE + FSLASH + SINGLESPACE

        return options_result

    def _produce_variable(self, input_variable):

        variable_result = ""

        variable_result = NEWLINE + self.configs.variable_decorator + input_variable.get_name()

        # produce the options
        prod_opts = self._produce_options(input_variable.get_options())
        if len(prod_opts) > 0:
            variable_result = ("%s %s" %  (variable_result, prod_opts))

        # add the variable's value - if it has it
        if input_variable.get_value() is not None:
            var_escaped_value = ""
            if input_variable.get_value() != "":
                v, r = miniparse.escape(input_variable.get_value(), BSLASH, [QUOTE])
                if not v:
                    return None
                var_escaped_value = r

            variable_result += SINGLESPACE + EQSIGN + SINGLESPACE + QUOTE + var_escaped_value + QUOTE

        return variable_result

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
