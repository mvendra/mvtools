#!/usr/bin/env python

import sys
import os

import path_utils
import miniparse
import mvtools_exception

# string parsing
COMMENTS_SINGLE = ["#", "//"]
COMMENT_MULTI = ("/*", "*/")

# basic types - values
DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE = 1
DSLTYPE20_ENTRY_VALUE_TYPE_PLUS = 2
DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR = 3

# basic types - general
DSLTYPE20_ENTRY_TYPE_VAR = 1
DSLTYPE20_ENTRY_TYPE_OPT = 2
DSLTYPE20_ENTRY_TYPE_CTX = 3

def hasopt_opts(opts, optname):
    for o in opts:
        if o[0] == optname:
            return True
    return False

def hasopt_var(var, optname):
    for o in var[2]:
        if o[0] == optname:
            return True
    return False

def convert_var_obj_list_to_neutral_format(var_obj_list):
    return [(x.get_name(), x.get_value_resolved(), [(y.get_name(), y.get_value_resolved()) for y in x.get_options()]) for x in var_obj_list]

def convert_opt_obj_list_to_neutral_format(opt_obj_list):
    return [(x.get_name(), x.get_value_resolved()) for x in opt_obj_list]

def make_obj_opt_list_from_neutral_format(configs, options):

    result = []

    if options is None:
        return True, None

    if isinstance(options, DSLType20_Option):
        return True, None

    if not isinstance(options, list):
        return False, "Options [%s] are invalid" % options

    opt_name_map = {}
    for opt in options:

        if not isinstance(opt, tuple):
            return False, "Option [%s] is not a tuple" % opt
        opt_name, opt_val = opt

        if opt_name in opt_name_map:
            return False, "Duplicated option: [%s]" % opt_name
        opt_name_map[opt_name] = True

        try:
            opt_obj = DSLType20_Option(configs, opt_name)
            if opt_val is not None:
                if isinstance(opt_val, list):
                    for x in opt_val:
                        if x is None:
                            return False, "Invalid option value in: [%s]" % opt_val
                        opt_obj.new_value()
                        opt_obj.add_value_immediate(x)
                else:
                    opt_obj.new_value()
                    opt_obj.add_value_immediate(opt_val)
            result.append(opt_obj)
        except mvtools_exception.mvtools_exception as ex:
            return False, ex.get_message()

    return True, result

def read_list_top_prev(target_list):
    return target_list[len(target_list)-2]

def read_list_top(target_list):
    return target_list[len(target_list)-1]

def write_list_top(target_list, val):
    target_list[len(target_list)-1] = val

def expand_value_single(configs, str_input):

    if str_input is None:
        return True, None

    if not isinstance(str_input, str):
        return False, str_input

    local_str_input = str_input

    if configs.expand_user:
        local_str_input = os.path.expanduser(local_str_input)
        if miniparse.TILDA in local_str_input:
            return False, str_input

    return True, local_str_input

def sanitize_line(line_in, multiline_comment_flag):

    # first input
    line_out = line_in.strip()

    # finish multiline comment
    if multiline_comment_flag:

        pr = line_out.find(COMMENT_MULTI[1])
        if pr == -1:
            return "", True
        line_out = (line_out[pr + len(COMMENT_MULTI[1]):]).strip()

    if line_out == "":
        return "", False

    # process comments (single / multi)
    while True:

        ps = []
        for c in COMMENTS_SINGLE:
            ps_temp = miniparse.guarded_find(line_out, c, miniparse.QUOTE, miniparse.BSLASH)
            if ps_temp is None:
                return None, False
            if ps_temp > -1:
                ps.append((c, ps_temp))

        pl = miniparse.guarded_find(line_out, COMMENT_MULTI[0], miniparse.QUOTE, miniparse.BSLASH)
        if pl is None:
            return None, False

        pr = miniparse.guarded_find(line_out, COMMENT_MULTI[1], miniparse.QUOTE, miniparse.BSLASH)
        if pr is None:
            return None, False

        # try to process a single-line comment
        pc = None
        for p in ps:

            if pl > -1:

                if pc is None:
                    if p[1] < pl:
                        pc = p
                else:
                    if p[1] < pc[1] and p[1] < pl:
                        pc = p

            else:

                if pc is None:
                    pc = p
                else:
                    if p[1] < pc[1]:
                        pc = p

        if pc is not None:
            line_out = (line_out[:pc[1]]).strip()
            if line_out == "":
                return "", False
            continue

        # try to process a multi-line comment
        if pl > -1:

            if pr > -1:
                if pr < pl:
                    return None, False

                line_out = (line_out[:pl] + line_out[pr + len(COMMENT_MULTI[1]):]).strip()

            else:
                line_out = (line_out[:pl]).strip()
                return line_out, True

        else:

            if pr > -1:
                return None, False
            break

    return line_out.strip(), False

def validate_name(name):

    if name is None:
        return False

    if not isinstance(name, str):
        return False

    if not len(name) >= 1:
        return False

    if not miniparse.scan_simple(name, miniparse.IDENTIFIER):
        return False

    return True

def _validate_value_single(value_str):

    if not isinstance(value_str, str):
        return False

    if miniparse.NEWLINE in value_str:
        return False

    if miniparse.NULL in value_str:
        return False

    return True

def validate_options(options):

    if options is None:
        return True, None

    if isinstance(options, DSLType20_Option):
        return True, None

    if not isinstance(options, list):
        return False, "Options [%s] are invalid" % options

    opt_name_map = {}
    for x in options:

        if not isinstance(x, DSLType20_Option):
            return False, "Option [%s] is invalid" % x

        if x.get_name() in opt_name_map:
            return False, "Duplicated option: [%s]" % x
        opt_name_map[x.get_name()] = True

    return True, None

def opt_list_has(options, name):

    for opt in options:
        if opt.get_name() == name:
            return True, opt
    return False, None

def inherit_options_helper(parent_options, new_options):

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
            if r.get_value_resolved() is None and n_opt.get_value_resolved() is None:
                continue # doubletapped, valueless option. drop/skip
        result.append(n_opt)

    return result

class DSLType20_Value:

    def __init__(self, configs):
        self.configs = configs
        self.internal_data = []

    def add_immediate(self, source):
        if not _validate_value_single(source):
            raise mvtools_exception.mvtools_exception("Invalid value [%s]" % source)
        self.internal_data.append((DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, source))

    def add_plus(self):
        self.internal_data.append((DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None))

    def add_envvar(self, source):
        self.internal_data.append((DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, source))

    def get_resolved(self):

        result = None
        if len(self.internal_data) > 0:
            result = ""

        for v in self.internal_data:

            v_res = ""
            if v[0] == DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE:
                v_res = v[1]
            elif v[0] == DSLTYPE20_ENTRY_VALUE_TYPE_PLUS:
                pass
            elif v[0] == DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR:
                try:
                    v_res = os.environ[v[1]]
                except KeyError as ex:
                    raise mvtools_exception.mvtools_exception("Unable to resolve envvar [%s]" % v[1])

            if self.configs.expand_user:
                v_res = os.path.expanduser(v_res)
                if miniparse.TILDA in v_res:
                    raise mvtools_exception.mvtools_exception("Unable to expand user [%s]" % v_res)
            result += v_res

        return result

    def get_serialized(self):

        result = None
        if len(self.internal_data) > 0:
            result = ""

        for v in self.internal_data:

            v_res = ""
            if v[0] == DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE:

                if v[1] != "":
                    v, r = miniparse.escape(v[1], miniparse.BSLASH, [miniparse.QUOTE])
                    if not v:
                        raise mvtools_exception.mvtools_exception("Unable to ecape value [%s]" % v[1])
                    v_res = r
                v_res = miniparse.QUOTE + v_res + miniparse.QUOTE

            elif v[0] == DSLTYPE20_ENTRY_VALUE_TYPE_PLUS:
                v_res = "%s%s%s" % (miniparse.SINGLESPACE, miniparse.PLUSSIGN, miniparse.SINGLESPACE)
            elif v[0] == DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR:
                v_res = "%s%s" % (miniparse.DOLLARSIGN, v[1])
            result += v_res

        return result

class DSLType20_ValueHolder:

    def __init__(self, configs):
        self.configs = configs

    def new_value(self):

        if self.value is None:
            self.value = DSLType20_Value(self.configs)
        elif isinstance(self.value, DSLType20_Value):
            self.value = [self.value, DSLType20_Value(self.configs)]
        else:
            self.value.append(DSLType20_Value(self.configs))

    def add_value_immediate(self, value):

        val_ptr = None
        if self.value is None:
            raise mvtools_exception.mvtools_exception("Immediate value [%s] cannot be added - value container is empty" % value)
        elif isinstance(self.value, DSLType20_Value):
            val_ptr = self.value
        else:
            val_ptr = self.value[len(self.value)-1]

        if len(val_ptr.internal_data) > 0:
            val_ptr.add_plus()
        val_ptr.add_immediate(value)

    def add_value_envvar(self, envvar):

        val_ptr = None
        if self.value is None:
            raise mvtools_exception.mvtools_exception("Environment variable [%s] cannot be added - value container is empty" % envvar)
        elif isinstance(self.value, DSLType20_Value):
            val_ptr = self.value
        else:
            val_ptr = self.value[len(self.value)-1]

        if len(val_ptr.internal_data) > 0:
            val_ptr.add_plus()
        val_ptr.add_envvar(envvar)

    def get_value_resolved(self):

        if self.value is None:
            return None
        elif isinstance(self.value, DSLType20_Value):
            return self.value.get_resolved()

        result = []
        for e in self.value:
            res_str = e.get_resolved()
            result.append(res_str)
        return result

    def get_value_serialized(self):

        if self.value is None:
            return None
        elif isinstance(self.value, DSLType20_Value):
            return self.value.get_serialized()

        add_comma = False
        result = miniparse.LPARENT
        for e in self.value:
            if add_comma:
                result += "%s%s" % (miniparse.COMMA, miniparse.SINGLESPACE)
            result += e.get_serialized()
            add_comma = True
        result += miniparse.RPARENT
        return result

class DSLType20_Variable(DSLType20_ValueHolder):

    def __init__(self, configs, name, options):

        super().__init__(configs)

        self.name = name
        self.value = None
        self.options = options

        if not validate_name(self.name):
            raise mvtools_exception.mvtools_exception("Variable name is invalid")

        v, r = validate_options(self.options)
        if not v:
            raise mvtools_exception.mvtools_exception("Options are invalid: [%s]" % r)

    def get_type(self):
        return DSLTYPE20_ENTRY_TYPE_VAR

    def get_name(self):
        return self.name

    def get_options(self):
        if self.options is None:
            return []
        if isinstance(self.options, DSLType20_Option):
            return [self.options]
        return self.options

class DSLType20_Option(DSLType20_ValueHolder):

    def __init__(self, configs, name):

        super().__init__(configs)

        self.name = name
        self.value = None

        if not validate_name(self.name):
            raise mvtools_exception.mvtools_exception("Option name is invalid")

    def get_type(self):
        return DSLTYPE20_ENTRY_TYPE_OPT

    def get_name(self):
        return self.name

class DSLType20_Context:

    def __init__(self, ptr_parent, name, options):

        self.ptr_parent = ptr_parent
        self.name = name
        self.options = options
        self.entries = []

        if not validate_name(self.name):
            raise mvtools_exception.mvtools_exception("Context name is invalid")

        v, r = validate_options(self.options)
        if not v:
            raise mvtools_exception.mvtools_exception("Options are invalid: [%s]" % r)

    def get_type(self):
        return DSLTYPE20_ENTRY_TYPE_CTX

    def get_parent_ptr(self):
        return self.ptr_parent

    def get_name(self):
        return self.name

    def get_options(self):
        if self.options is None:
            return []
        if isinstance(self.options, DSLType20_Option):
            return [self.options]
        return self.options

    def get_entries(self):
        return self.entries

    def add_entry(self, new_entry):
        self.entries.append(new_entry)

class DSLType20_Config:

    def __init__(self, expand_user = False, allow_var_dupes = True, inherit_options = False, var_decorator = ""):

        self.expand_user = expand_user
        self.allow_var_dupes = allow_var_dupes
        self.inherit_options = inherit_options
        self.var_decorator = var_decorator

class _internal_parse_context:

    def __init__(self):
        self.bracket_stack = [] # 1 means "assumed pseudo context", 2 means "surely pseudo context", 3 means "named/regular context"
        self.context_stack = [None]

INTERNAL_DFS_CONTEXT_DEPTH_SENTINEL_MAX = 200
class internal_dfs_context:

    def __init__(self, init_node):
        self.current_node = init_node
        self.vars = []
        self.ctxs = []
        self.all = []
        self.depth_sentinel = 0

class DSLType20:

    def __init__(self, _configs):

        # internal
        self.data = None
        self.root_context_id = "_DSL_TYPE20_RESERVED_INTERNAL_MASTER_ROOT_CONTEXT_"
        self.max_number_options = 1024
        self.indent = ""
        self.clear()

        # read configs
        self.configs = _configs

    def clear(self):
        self.data = None
        self.data = DSLType20_Context(None, self.root_context_id, None)

    def get_entire_dfs(self):

        dfs_ctx = internal_dfs_context(self.data)
        try:
            if not self._get_entire_dfs(dfs_ctx):
                return False, "Recursive traversal failed"
        except mvtools_exception.mvtools_exception as ex:
            return False, "Recursive traversal failed: [%s]" % ex.get_message()
        return True, dfs_ctx.all

    def add_context(self, ctx_name, ctx_options, parent_ctx = None):

        if ctx_name == self.root_context_id:
            return False, "Tried to add context: [%s] - error. This is a reserved context name" % (self.root_context_id)

        if parent_ctx is None:
            parent_ctx = self.root_context_id

        # pre-validate context name
        if not validate_name(ctx_name):
            return False, "Invalid context name: [%s]" % ctx_name

        # pre-validate options
        v, r = validate_options(ctx_options)
        if not v:
            return False, r

        # first check if the context doesn't already exist
        v, r = self._find_context(ctx_name, None, None)
        if not v:
            return False, r
        if r:
            return False, "Failed adding new context: [%s] already exists" % ctx_name

        # add new context to the internal datastructure
        v, r = self._find_context(parent_ctx, self._add_ctx_helper, (ctx_name, ctx_options))
        if not v:
            return False, r
        if not r:
            return False, "Unable to add context [%s] to [%s] - the latter cannot be found." % (ctx_name, parent_ctx)

        return True, None

    def get_context(self, context_name = None):

        if context_name is None or context_name == self.root_context_id:
            return True, self._ctx_shallow_copy(None, self.data)

        v, r = self._get_context_internal(context_name, True, None)
        if not v:
            return False, r
        if len(r) == 0:
            r = None
        else:
            r = r[0]
        return True, r

    def get_all_contexts_dfs(self):

        dfs_ctx = internal_dfs_context(self.data)
        try:
            if not self._get_all_contexts_dfs(dfs_ctx):
                return False, "Recursive traversal failed"
        except mvtools_exception.mvtools_exception as ex:
            return False, "Recursive traversal failed: [%s]" % ex.get_message()
        return True, dfs_ctx.ctxs

    def get_all_sub_contexts(self, parent_context = None):
        return self._get_context_internal(None, False, parent_context)

    def get_sub_context(self, context_name, parent_context = None):

        if context_name is None or context_name == self.root_context_id:
            return True, self._ctx_shallow_copy(None, self.data)

        v, r = self._get_context_internal(context_name, False, parent_context)
        if not v:
            return False, r
        if len(r) == 0:
            r = None
        else:
            r = r[0]
        return True, r

    def rem_context(self, context_name):

        ctx_info = []

        if context_name is None or context_name == self.root_context_id:
            return False, "Removing the root context is forbidden"

        v, r = self._find_context(context_name, self._rem_context_helper, ctx_info)
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context_name

        if len(ctx_info) != 1:
            return False, "Found more than one instance of context [%s]. Fatal error." % context_name

        ctx_parent = ctx_info[0].get_parent_ptr()
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

    def add_variable(self, variable, context = None):

        # pre-validate variable
        if not isinstance(variable, DSLType20_Variable):
            return False, "Wrong input variable type"

        # add context to the root context if it does not preexist
        if context is None:
            context = self.root_context_id
        else:
            self.add_context(context, [], None)

        # add new variable to internal data
        v, r = self._find_context(context, self._add_variable_helper, variable)
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context
        return True, None

    def get_all_variables_dfs(self):

        dfs_ctx = internal_dfs_context(self.data)
        try:
            if not self._get_all_variables_dfs(dfs_ctx):
                return False, "Recursive traversal failed"
        except mvtools_exception.mvtools_exception as ex:
            return False, "Recursive traversal failed: [%s]" % ex.get_message()
        return True, dfs_ctx.vars

    def get_all_variables(self, context = None):
        return self.get_variables(None, context)

    def get_variables(self, varname, context = None):

        if context is None:
            context = self.root_context_id
        result = []

        try:
            v, r = self._find_context(context, self._get_variable_helper, (varname, result))
            if not v:
                return False, r
            if not r:
                return False, "Context [%s] does not exist." % context
        except mvtools_exception.mvtools_exception as ex:
            return False, "Getting variables failed: [%s]" % ex.get_message()

        return True, result

    def rem_all_variables(self, context = None):
        return self._rem_variable_internal(None, context)

    def rem_variables(self, var_name, context = None):
        v, r = self._rem_variable_internal(var_name, context)
        if not v:
            return False, r
        return True, len(r)

    def parse(self, contents):

        self.clear()
        ipc = _internal_parse_context()
        lines = contents.replace(miniparse.WIN_NEWLINE, miniparse.NEWLINE).split(miniparse.NEWLINE)

        line_num = 0
        multiline_flag = False

        for line in lines:
            line_num += 1

            line_t, multiline_flag = sanitize_line(line, multiline_flag)
            if line_t is None:
                return False, "Unable to sanitize line: [%s]" % line
            if line_t == "":
                continue

            v, r = self._parse_line_delegate(ipc, line_t, line_num)
            if not v:
                return False, r

        if multiline_flag:
            return False, "Unterminated multiline comment"

        if len(ipc.bracket_stack) > 0:
            return False, "Unterminated context"

        return True, None

    def produce(self, _ctx_end_comment = False, _ctx_lvl_indent = False):

        result = ""
        self._clear_indent()
        # mvtodo: exception
        result += self._produce_context(self.data, _ctx_end_comment, _ctx_lvl_indent, True)
        return result.strip()

    def _get_entire_dfs(self, ctx):

        ctx.depth_sentinel += 1
        if ctx.depth_sentinel == INTERNAL_DFS_CONTEXT_DEPTH_SENTINEL_MAX:
            return False

        this_current_node = ctx.current_node
        ctx.all.append(self._ctx_shallow_copy(this_current_node.get_parent_ptr(), this_current_node))
        for entry in this_current_node.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR:
                ctx.all.append(self._var_copy(this_current_node, entry))
            elif entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                ctx.current_node = entry
                if not self._get_entire_dfs(ctx):
                    return False
                ctx.depth_sentinel -= 1

        return True

    def _get_all_contexts_dfs(self, ctx):

        ctx.depth_sentinel += 1
        if ctx.depth_sentinel == INTERNAL_DFS_CONTEXT_DEPTH_SENTINEL_MAX:
            return False

        this_current_node = ctx.current_node
        ctx.ctxs.append(self._ctx_shallow_copy(this_current_node.get_parent_ptr(), this_current_node))
        for entry in this_current_node.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                ctx.current_node = entry
                if not self._get_all_contexts_dfs(ctx):
                    return False
                ctx.depth_sentinel -= 1

        return True

    def _get_all_variables_dfs(self, ctx):

        ctx.depth_sentinel += 1
        if ctx.depth_sentinel == INTERNAL_DFS_CONTEXT_DEPTH_SENTINEL_MAX:
            return False

        this_current_node = ctx.current_node
        for entry in this_current_node.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR:
                ctx.vars.append(self._var_copy(this_current_node, entry))
            elif entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                ctx.current_node = entry
                if not self._get_all_variables_dfs(ctx):
                    return False
                ctx.depth_sentinel -= 1

        return True

    def _parse_line_delegate(self, ipc, current_line, current_line_number):

        # context name, begin
        if current_line == miniparse.LBRACKET:
            ipc.bracket_stack.append(1) # start by assuming this is going to be a pseudo context
            return True, None

        # context name, end
        if current_line == miniparse.RBRACKET:
            if len(ipc.bracket_stack) == 0:
                return False, "[%s]: Unstarted context" % current_line_number
            if read_list_top(ipc.bracket_stack) == 3: # only destack the TOS context if this was a named/regular context
                ipc.context_stack.pop()
            ipc.bracket_stack.pop()
            return True, None

        # context name, the name itself
        if current_line[0] == miniparse.ATSIGN:

            if len(ipc.bracket_stack) == 0:
                return False, "[%s]: Unstarted context: [%s]" % (current_line_number, current_line)

            if read_list_top(ipc.bracket_stack) == 2: # too late to define a name for this context
                return False, "[%s]: Context name must appear just after the opening bracket" % current_line_number

            if read_list_top(ipc.bracket_stack) == 3: # name already defined for this context
                return False, "[%s]: Context name is already defined - tried redefining [%s%s] with [%s]" % (current_line_number, miniparse.ATSIGN, read_list_top(ipc.context_stack), current_line)

            write_list_top(ipc.bracket_stack, 3) # TOS is now a named/regular context

            v, r = self._parse_context_name(current_line)
            if not v:
                return False, "[%s]: %s" % (current_line_number, r)
            parsed_context, parsed_context_options = r
            ipc.context_stack.append(parsed_context)
            v, r = self.add_context(read_list_top(ipc.context_stack), parsed_context_options, read_list_top_prev(ipc.context_stack))
            if not v:
                return False, "[%s]: Failed creating new context: [%s]." % (current_line_number, r)
            return True, None

        if len(ipc.bracket_stack) > 0: # skip root
            if read_list_top(ipc.bracket_stack) == 1:
                write_list_top(ipc.bracket_stack, 2) # TOS is now surely a pseudo context

        # variable
        v, r = self._parse_variable(current_line, read_list_top(ipc.context_stack))
        if not v:
            return False, "[%s]: %s" % (current_line_number, r)

        return True, None

    def _inherit_options(self, parent_ptr, child_ptr):

        if not self.configs.inherit_options:
            return child_ptr.get_options()

        aggregate_opts_list = []
        final_opts_list = []

        # aggregate all parents options up to root level
        current_parent_ptr = parent_ptr
        while (current_parent_ptr != None):
            aggregate_opts_list.append(current_parent_ptr.get_options())
            current_parent_ptr = current_parent_ptr.get_parent_ptr()

        # drop down inheriting options
        aggregate_opts_list.reverse()
        for opt_list_entry in aggregate_opts_list:
            final_opts_list = inherit_options_helper(final_opts_list, opt_list_entry)

        # and finally return whilst also combining in the child's own options
        return inherit_options_helper(final_opts_list, child_ptr.get_options())

    def _get_context_internal(self, context_name, find_itself, parent_context = None):

        if parent_context is None:
            parent_context = self.root_context_id

        if context_name == parent_context:
            return False, "Context [%s] and [%s] are the same" % (context_name, parent_context)

        result_ptr = []

        local_parent_context = parent_context
        if find_itself:
            local_parent_context = context_name

        try:
            v, r = self._find_context(local_parent_context, self._get_context_helper, (context_name, result_ptr, find_itself))
            if not v:
                return False, r
            if not r:
                return False, "Unable to return context [%s] of/from [%s] - context not found." % (context_name, parent_context)
        except mvtools_exception.mvtools_exception as ex:
            return False, "Unable to return context [%s] of/from [%s]: [%s]." % (context_name, parent_context, ex.get_message())

        return True, result_ptr

    def _rem_variable_internal(self, var_name, context = None):

        if context is None:
            context = self.root_context_id
        result = []

        v, r = self._find_context(context, self._rem_variable_helper, (var_name, result))
        if not v:
            return False, r
        if not r:
            return False, "Context [%s] does not exist." % context
        return True, result

    def _context_exists(self, ctx_name):

        if ctx_name is None:
            ctx_name = self.root_context_id

        v, r = self._find_context(ctx_name, None, None)
        return v

    def _find_context(self, context_name, callback_func, callback_data):

        if context_name is None:
            context_name = self.root_context_id

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

        try:
            new_ctx = DSLType20_Context(ptr, cb_data_ctx[0], cb_data_ctx[1])
            ptr.add_entry(new_ctx)
            return True, None
        except mvtools_exception.mvtools_exception as ex:
            return False, ex.get_message()

    def _get_context_helper(self, ptr, cb_data_ctx):

        target_ctx_name, return_ptr, get_itself = cb_data_ctx

        if get_itself:
            return_ptr.append(self._ctx_shallow_copy(ptr.get_parent_ptr(), ptr))
            return True, None

        for entry in ptr.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX and (entry.get_name() == target_ctx_name or target_ctx_name is None):
                return_ptr.append(self._ctx_shallow_copy(ptr, entry))
                if target_ctx_name is not None:
                    break

        return True, None

    def _config_copy(self):
        return DSLType20_Config(self.configs.expand_user, self.configs.allow_var_dupes, self.configs.inherit_options, self.configs.var_decorator)

    def _val_copy(self, val_ptr):

        new_inst = DSLType20_Value(self._config_copy())
        for x in val_ptr.internal_data:

            if x[0] == DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE:
                new_inst.add_immediate(x[1])
            elif x[0] == DSLTYPE20_ENTRY_VALUE_TYPE_PLUS:
                new_inst.add_plus()
            elif x[0] == DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR:
                new_inst.add_envvar(x[1])
            else:
                raise mvtools_exception.mvtools_exception("Unexpected value type [%s]" % x)

        return new_inst

    def _obj_val_copy(self, obj_val_ptr):

        if obj_val_ptr is None:
            return None
        elif isinstance(obj_val_ptr, DSLType20_Value):
            return self._val_copy(obj_val_ptr)

        ret = []
        for x in obj_val_ptr:
            ret.append(self._val_copy(x))
        return ret

    def _var_copy(self, original_parent_ptr, var_ptr):
        new_inst = DSLType20_Variable(self._config_copy(), var_ptr.get_name(), self._opt_list_copy(self._inherit_options(original_parent_ptr, var_ptr)))
        new_inst.value = self._obj_val_copy(var_ptr.value)
        return new_inst

    def _ctx_hollow_copy(self, original_parent_ptr, target_ptr, ctx_ptr):
        return DSLType20_Context(target_ptr, ctx_ptr.get_name(), self._opt_list_copy(self._inherit_options(original_parent_ptr, ctx_ptr)))

    def _opt_copy(self, opt_ptr):
        new_inst = DSLType20_Option(self._config_copy(), opt_ptr.get_name())
        new_inst.value = self._obj_val_copy(opt_ptr.value)
        return new_inst

    def _opt_list_copy(self, opt_ptr_list):
        result = []
        for opt in opt_ptr_list:
            result.append(self._opt_copy(opt))
        return result

    def _generic_copy_helper(self, original_parent_ptr, target_ptr, entry_ptr):

        if entry_ptr.get_type() == DSLTYPE20_ENTRY_TYPE_VAR:
            return self._var_copy(original_parent_ptr, entry_ptr)
        elif entry_ptr.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
            return self._ctx_hollow_copy(original_parent_ptr, target_ptr, entry_ptr)

    def _ctx_shallow_copy(self, parent_ptr, ctx_ptr):

        # creates a "shallow-ish" copy - child contexts are also copied, but hollowed

        ctx_copy = DSLType20_Context(None, ctx_ptr.get_name(), self._opt_list_copy(self._inherit_options(parent_ptr, ctx_ptr)))
        for ent in ctx_ptr.get_entries():
            ctx_copy.add_entry(self._generic_copy_helper(ctx_ptr, ctx_copy, ent))
        return ctx_copy

    def _rem_context_helper(self, ptr, cb_data_rem):

        cb_data_rem.append(ptr)
        return True, None

    def _add_variable_helper(self, ptr, cb_data_add):

        if not self.configs.allow_var_dupes:
            for entry in ptr.get_entries():
                if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR and entry.get_name() == cb_data_add.get_name():
                    return False, "Variable [%s] already exists" % cb_data_add.get_name()

        ptr.add_entry(cb_data_add)
        return True, None

    def _get_variable_helper(self, ptr, cb_data_get):

        var_name, list_ptr = cb_data_get

        for entry in ptr.get_entries():
            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR and (entry.get_name() == var_name or var_name is None):
                list_ptr.append(self._var_copy(ptr, entry))

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
        parsed_opts = None

        v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.ATSIGN + miniparse.ANYSPACE + miniparse.IDENTIFIER)
        if not v:
            return False, "Malformed context name: [%s]." % str_input
        parsed_context_name = (r[0]).strip()
        local_str_input = (r[1]).strip()

        if not local_str_input == "": # there might be options

            v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.ANYSPACE + miniparse.LCBRACKET)

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
        v, r = miniparse.remove_next_of(parsed_context_name, miniparse.ATSIGN)
        if not v:
            return False, "Malformed context name: [%s]." % parsed_context_name
        parsed_context_name = r.strip()

        return True, (parsed_context_name, parsed_opts)

    def _parse_variable(self, str_input, context = None):

        var_inst = None
        try:
            var_inst = DSLType20_Variable(self.configs, "dummy-name", None)
        except mvtools_exception.mvtools_exception as ex:
            return False, "Unable to parse variable [%s]: [%s]" % (str_input, ex.get_message())

        var_name = None
        parsed_opts = None

        local_str_input = str_input.strip()

        if self.configs.var_decorator != "":
            if local_str_input.find(self.configs.var_decorator) != 0:
                return False, "Can't parse variable: [%s]: Decorator [%s] not found." % (str_input, self.configs.var_decorator)
            local_str_input = (local_str_input[len(self.configs.var_decorator):]).strip()

        local_context = self.root_context_id
        if context is not None:
            local_context = context
        if not self._context_exists(local_context):
            return False, "Can't parse variable: [%s]: Context doesn't exist: [%s]." % (str_input, context)

        # start by parsing the variable's value - if it has it
        v, r = self._parse_value_end(local_str_input, var_inst)
        if not v:
            return False, "Can't parse variable: [%s]: [%s]." % (str_input, r)
        local_str_input = r

        v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.IDENTIFIER + miniparse.ANYSPACE + miniparse.LCBRACKET)
        if v:

            # variable has options

            var_name = r[0].strip()
            local_str_input = r[1].strip()

            v, r = miniparse.remove_last_of(var_name, miniparse.LCBRACKET)
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

            v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.IDENTIFIER + miniparse.ANYSPACE)
            if not v:
                return False, "Malformed variable: [%s]: Can't parse variable name." % str_input
            var_name = (r[0]).strip()
            local_str_input = (r[1]).strip()

            if len(local_str_input) != 0:
                return False, "Malformed variable: [%s]: Remaining unparseable contents: [%s]." % (str_input, local_str_input)

        var_inst.name = var_name
        var_inst.options = parsed_opts
        v, r = self.add_variable(var_inst, local_context)
        if not v:
            return False, "Unable to add variable [%s]: [%s]" % (var_name, r)

        return True, None

    def _parse_value_end(self, whole_str_input, var_inst):

        local_str_input = whole_str_input
        eqsign_expected = False

        v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.ESCAPED_RPARENT)
        if v: # value is a string list

            local_str_input = (r[1]).strip()
            eqsign_expected = True

            while_sentinel = 0
            while True:
                while_sentinel += 1

                if while_sentinel == 500:
                    return False, "Unable to finish parsing variable: [%s] has too many values." % whole_str_input

                v, r = self._parse_value_end_single(local_str_input, var_inst)
                if not v:
                    return False, r
                local_str_input = (r[0]).strip()

                if not r[1]: # no value returned - only legal when empty parens used
                    v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.ESCAPED_LPARENT)
                    if not v:
                        return False, "Unable to parse variable value: [%s] empty value slot." % whole_str_input

                # try to parse comma, if present
                v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.COMMA)
                if not v:
                    break
                local_str_input = (r[1]).strip()

            # remove enclosing left parenthesis
            v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.ESCAPED_LPARENT)
            if not v:
                return False, "Malformed variable: [%s]: string-list value must be be enclosed with parentheses (failed at the second/left parenthesis)." % whole_str_input
            local_str_input = (r[1]).strip()

            if isinstance(var_inst.value, list):
                var_inst.value.reverse()

        else: # value is either None (valueless) or a single string

            v, r = self._parse_value_end_single(whole_str_input, var_inst)
            if not v:
                return False, r
            local_str_input = (r[0]).strip()
            eqsign_expected = r[1]

        # remove equal sign just before the variable's value
        if eqsign_expected:
            v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.EQSIGN)
            if not v:
                return False, "Malformed variable: [%s]: Failed to parse the equal sign before the variable's value." % whole_str_input
            local_str_input = (r[1]).strip()

        return True, local_str_input

    def _parse_value_end_single(self, str_input, var_inst):

        local_str_input = str_input.strip()
        eqsign_expected = False
        add_new = True
        plus_state_flag = None
        plus_required = None

        while_sentinel = 0
        while True:
            while_sentinel += 1

            if while_sentinel == 500:
                return False, "Unable to finish parsing variable: [%s] has too many (inline) values" % str_input

            v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.QUOTE + miniparse.ANYSPACE)
            if v: # new immediate value

                if plus_required:
                    return False, "Malformed variable: [%s]: values should be joined with an intermediary plus sign (processing immediate value)." % str_input
                plus_required = True
                plus_state_flag = False
                eqsign_expected = True

                if r[1][len(r[1])-1] == miniparse.BSLASH: # variable value was indeed enclosed with quotes, but the last quote was escaped. error.
                    return False, "Malformed variable: [%s]: value must be be enclosed with a nonescaped quote (failed at the second quote)." % str_input
                local_str_input = r[1]

                # find next nonescaped quote in reverse (beginning of the value)
                v, r = miniparse.last_not_escaped_slice(local_str_input, miniparse.QUOTE, miniparse.BSLASH)
                if not v:
                    return False, "Malformed variable: [%s]: can't find first quote of the variable's value." % str_input
                local_str_input = (r[1]).strip()
                var_value = r[0]

                # descape the variable's value
                v, r = miniparse.descape(var_value, miniparse.BSLASH)
                if not v:
                    return False, "Variable descaping failed: [%s]" % var_value
                var_value = r

                # remove first quote of value
                v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.QUOTE)
                if not v:
                    return False, "Malformed variable: [%s]: value must be enclosed with quotes." % str_input
                local_str_input = (r[1]).strip()

                if add_new:
                    var_inst.new_value()
                    add_new = False

                try:
                    var_inst.add_value_immediate(var_value)
                except mvtools_exception.mvtools_exception as ex:
                    return False, "Unable to parse variable value [%s]: [%s]." % (str_input, ex.get_message())
                continue

            v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.IDENTIFIER + miniparse.ANYSPACE)
            if v: # new envvar

                if (r[1]).strip() == "": # false positive - valueless variable
                    break

                if plus_required:
                    return False, "Malformed variable: [%s]: values should be joined with an intermediary plus sign (processing envvar)." % str_input
                plus_required = True
                plus_state_flag = False
                eqsign_expected = True

                envvar_name = r[0]
                local_str_input = r[1]

                # remove dollar sign
                v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.ESCAPED_DOLLARSIGN)
                if not v:
                    return False, "Malformed variable: [%s]: envvar must be preceded with a dollar sign." % str_input
                local_str_input = (r[1]).strip()

                if add_new:
                    var_inst.new_value()
                    add_new = False

                try:
                    var_inst.add_value_envvar(envvar_name)
                except mvtools_exception.mvtools_exception as ex:
                    return False, "Unable to parse variable value [%s]: [%s]." % (str_input, ex.get_message())
                continue

            v, r = miniparse.scan_and_slice_end(local_str_input, miniparse.ESCAPED_PLUSSIGN + miniparse.ANYSPACE)
            if v: # new plus sign

                if (plus_state_flag is None) or (plus_state_flag is True):
                    return False, "Malformed variable: [%s]: unexpected plus sign." % str_input
                plus_state_flag = True
                plus_required = False
                local_str_input = (r[1]).strip()
                continue

            break # something else - break out

        if plus_state_flag:
            return False, "Malformed variable: [%s]: Leftover plus sign." % str_input

        if isinstance(var_inst.value, DSLType20_Value):
            var_inst.value.internal_data.reverse()
        elif isinstance(var_inst.value, list):
            var_inst.value[len(var_inst.value)-1].internal_data.reverse()

        return True, (local_str_input, eqsign_expected)

    def _parse_options(self, str_input):

        local_str_input = str_input.strip()

        opt_name = None
        opt_val = None
        parsed_opts = None

        if local_str_input == miniparse.RCBRACKET: # tolerate empty option list
            return True, None, ""

        counter = -1
        while True:
            counter += 1

            if counter >= self.max_number_options:
                return False, "Failed parsing options: [%s]. Maximum number of options exceeded: [%s]." % (str_input, self.max_number_options), None

            try:
                v, r1, r2, r3 = self._parse_next_option(local_str_input)
                if not v:
                    return False, "Failed parsing options: [%s]" % r1, None
            except mvtools_exception.mvtools_exception as ex:
                return False, "Failed parsing options: [%s]" % ex.get_message()

            if parsed_opts is None:
                parsed_opts = r1
            elif isinstance(parsed_opts, DSLType20_Option):
                parsed_opts = [parsed_opts, r1]
            else:
                parsed_opts.append(r1)
            local_str_input = r2
            if not r3: # there are no more options
                break

        return True, parsed_opts, local_str_input

    def _parse_next_option(self, str_input):

        opt_inst = None
        opt_name = None
        more_options = None

        local_str_input = str_input.strip()
        if local_str_input == "":
            return False, "Invalid option input: [%s]" % str_input, None, None

        # start by parsing the option's name
        v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.IDENTIFIER + miniparse.ANYSPACE + miniparse.COLON)
        if v:

            # option has value

            opt_name = (r[0]).strip()
            local_str_input = (r[1]).strip()

            # remove the colon off the option's name
            v, r = miniparse.remove_last_of(opt_name, miniparse.COLON)
            if not v:
                return False, "Failed parsing options: [%s]" % str_input, None, None
            opt_name = r.strip()
            opt_inst = DSLType20_Option(self.configs, opt_name)

            v, r = self._parse_value(str_input, local_str_input, opt_inst)
            if not v:
                return False, r, None, None
            local_str_input = r.strip()

            # need to advance past this option to look ahead for the next
            v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.FSLASH)
            more_options = v

            if more_options:
                local_str_input = (r[1]).strip()
            if not more_options:

                # there are no other options

                v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.RCBRACKET)
                if not v:
                    return False, "Parsing option failed: [%s]" % str_input, None, None
                local_str_input = (r[1]).strip()

        else:

            # option has no value

            rem_last_chr = miniparse.FSLASH
            v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.IDENTIFIER + miniparse.ANYSPACE + miniparse.FSLASH)
            more_options = v
            if not more_options:

                # there are no other options

                v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.IDENTIFIER + miniparse.ANYSPACE + miniparse.RCBRACKET)
                if not v:
                    return False, "Parsing option failed: [%s]" % str_input, None, None
                local_str_input = (r[1]).strip()
                rem_last_chr = miniparse.RCBRACKET

            else:
                local_str_input = (r[1]).strip()

            opt_name = (r[0]).strip()
            v, r = miniparse.remove_last_of(opt_name, rem_last_chr)
            if not v:
                return False, "Parsing option failed: [%s]" % str_input, None, None
            opt_name = r.strip()
            opt_inst = DSLType20_Option(self.configs, opt_name)

        return True, opt_inst, local_str_input, more_options

    def _parse_value(self, str_input, local_str_input, opt_inst):

        v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.ESCAPED_LPARENT)
        if v:

            # option value is a stringlist
            local_str_input = (r[1]).strip()

            r_paren_allowed = True
            while_sentinel = 0
            while True:
                while_sentinel += 1

                if while_sentinel == 500:
                    return False, "Failed parsing options: [%s]" % str_input

                # checks if the right parenthesis has been reached
                v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.ESCAPED_RPARENT)
                if v:
                    if not r_paren_allowed:
                        return False, "Failed parsing options: [%s]" % str_input
                    local_str_input = (r[1]).strip()
                    break

                # read out current value
                v, r = self._parse_value_single(str_input, local_str_input, opt_inst)
                if not v:
                    return False, r
                local_str_input = r.strip()

                # try to parse comma, if present
                v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.COMMA)
                if v:
                    local_str_input = (r[1]).strip()
                r_paren_allowed = not v

        else:

            v, r = self._parse_value_single(str_input, local_str_input, opt_inst)
            if not v:
                return False, r
            local_str_input = r.strip()

        return True, local_str_input

    def _parse_value_single(self, str_input, local_str_input, opt_inst):

        local_str_input = local_str_input.strip()
        add_new = True
        plus_state_flag = None
        plus_required = None

        while_sentinel = 0
        while True:
            while_sentinel += 1

            if while_sentinel == 500:
                return False, "Failed parsing options: [%s]" % str_input

            v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.QUOTE) # find next quote (option's value - first)
            if v: # new immediate value

                if plus_required:
                    return False, "Malformed option: [%s]: values should be joined with an intermediary plus sign (processing immediate value)." % str_input
                plus_required = True
                plus_state_flag = False
                local_str_input = (r[1]).rstrip()

                # forward until closing quote is found (the next not escaped)
                v, r = miniparse.next_not_escaped_slice(local_str_input, miniparse.QUOTE, miniparse.BSLASH)
                if not v:
                    return False, "Failed parsing options: [%s]" % str_input
                opt_val = r[0]
                local_str_input = (r[1]).strip()

                v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.QUOTE) # find next quote (option's value - second)
                if not v:
                    return False, "Failed parsing options: [%s]" % str_input
                local_str_input = (r[1]).strip()

                # descape the value, and its ready for storage
                v, r = miniparse.descape(opt_val, miniparse.BSLASH)
                if not v:
                    return False, "Failed parsing options: [%s]" % str_input
                opt_val = r

                if add_new:
                    opt_inst.new_value()
                    add_new = False

                # mvtodo: exception
                opt_inst.add_value_immediate(opt_val)
                continue

            v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.ESCAPED_DOLLARSIGN)
            if v: # new envvar

                if plus_required:
                    return False, "Malformed option: [%s]: values should be joined with an intermediary plus sign (processing envvar)." % str_input
                plus_required = True
                plus_state_flag = False
                local_str_input = (r[1]).lstrip()

                v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.IDENTIFIER)
                if not v:
                    return False, "Malformed option: [%s]: No (envvar) identifier after dollar sign." % str_input

                envvar_name = r[0]
                local_str_input = (r[1]).lstrip()

                if add_new:
                    opt_inst.new_value()
                    add_new = False

                # mvtodo: exception
                opt_inst.add_value_envvar(envvar_name)
                continue

            v, r = miniparse.scan_and_slice_beginning(local_str_input, miniparse.ESCAPED_PLUSSIGN)
            if v: # new plus sign

                if (plus_state_flag is None) or (plus_state_flag is True):
                    return False, "Malformed option: [%s]: unexpected plus sign." % str_input
                plus_state_flag = True
                plus_required = False
                local_str_input = (r[1]).strip()
                continue

            break # something else - break out

        if plus_state_flag:
            return False, "Malformed option: [%s]: Leftover plus sign." % str_input

        return True, local_str_input

    def _produce_context(self, context, _ctx_end_comment, _ctx_lvl_indent, _indent_skip = False):

        if context is None:
            return None

        end_comment = ""
        result = ""
        local_indent = ""

        if _ctx_lvl_indent and context.get_name() != self.root_context_id and not _indent_skip:
            self._inc_indent()
            local_indent = self.indent

        if context.get_name() != self.root_context_id:
            result += (miniparse.NEWLINE + local_indent + miniparse.LBRACKET + miniparse.NEWLINE + local_indent + miniparse.ATSIGN + context.get_name() + (" %s" % ( self._produce_options(context.get_options()) ) )).rstrip()
            if _ctx_end_comment:
                end_comment = "%s%s%s%s%s" % (miniparse.SINGLESPACE, COMMENTS_SINGLE[0], miniparse.SINGLESPACE, miniparse.ATSIGN, context.get_name())

        ctx_prev = False
        idx = 0
        for entry in context.get_entries():
            idx += 1

            ctx_newline_maybe = miniparse.NEWLINE

            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_VAR:
                var_prod = self._produce_variable(entry)
                if var_prod is None:
                    return None
                result += miniparse.NEWLINE + local_indent + var_prod
                ctx_prev = False

            if entry.get_type() == DSLTYPE20_ENTRY_TYPE_CTX:
                if idx > 1 and ctx_prev:
                    ctx_newline_maybe = ""
                result += ctx_newline_maybe + self._produce_context(entry, _ctx_end_comment, _ctx_lvl_indent, (context.get_name() == self.root_context_id))
                ctx_prev = True

        if context.get_name() != self.root_context_id:
            result += miniparse.NEWLINE + local_indent + miniparse.RBRACKET + end_comment + miniparse.NEWLINE

        if _ctx_lvl_indent:
            self._dec_indent()

        return result

    def _produce_options(self, input_options):

        options_result = ""

        idx = 0
        for opt in input_options:
            idx += 1

            if idx == 1:
                options_result += miniparse.LCBRACKET

            options_result += opt.get_name()

            if opt.get_value_resolved() is not None:

                # option has value
                options_result += miniparse.COLON + miniparse.SINGLESPACE
                options_result += opt.get_value_serialized()

            if idx == len(input_options):
                options_result += miniparse.RCBRACKET
            else:
                options_result += miniparse.SINGLESPACE + miniparse.FSLASH + miniparse.SINGLESPACE

        return options_result

    def _produce_variable(self, input_variable):

        variable_result = ""
        variable_result = self.configs.var_decorator + input_variable.get_name()

        # produce the options
        prod_opts = self._produce_options(input_variable.get_options())
        if len(prod_opts) > 0:
            variable_result = ("%s %s" %  (variable_result, prod_opts))

        # add the variable's value - if it has it
        if input_variable.get_value_resolved() is not None:

            variable_result += miniparse.SINGLESPACE + miniparse.EQSIGN + miniparse.SINGLESPACE
            variable_result += input_variable.get_value_serialized()

        return variable_result

    def _inc_indent(self):
        self.indent += "    "

    def _dec_indent(self):
        if len(self.indent) > 0:
            self.indent = self.indent[:-4]

    def _clear_indent(self):
        self.indent = ""

def puaq(selfhelp):
    print("Usage: %s [--decorator the-deco] file_to_parse.t20" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    the_deco = ""
    file_to_parse = sys.argv[1]
    if file_to_parse == "--decorator":
        the_deco = sys.argv[2]
        file_to_parse = sys.argv[3]

    dsl = DSLType20(DSLType20_Config(expand_user = True, allow_var_dupes = True, inherit_options = True, var_decorator = the_deco))

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
