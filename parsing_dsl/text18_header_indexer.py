#!/usr/bin/env python3

import sys
import os

import path_utils
import dsl_type20

PREFIX = "TEXT18_"
VAR_DECO = "* "

class ProdCtx:
    def __init__(self):
        self.ctx_counter = 0

    def get_counter(self):
        local_ctr_copy = self.ctx_counter
        self.ctx_counter += 1
        return local_ctr_copy

def fix_dash(line):
    line_fixed = ""
    for c in line:
        if c == "-":
            line_fixed += "_"
        else:
            line_fixed += c
    return line_fixed

def format_line_ctx(prefix, ctx, index):

    ctx_part = (ctx.get_name()).upper()
    ctx_part_fixed = fix_dash(ctx_part)

    return "%s%s %d" % (prefix, ctx_part_fixed, index)

def format_line_var(prefix, ctx, var, index):

    ctx_part = (ctx.get_name()).upper()
    ctx_part_fixed = fix_dash(ctx_part)

    var_part = (var.get_name()).upper()
    var_part_fixed = fix_dash(var_part)

    return "%s%s_%s %d" % (prefix, ctx_part_fixed, var_part_fixed, index)

def gen_from_t20(input_file, prod_ctx):

    t20_contents = ""
    gen_contents = ""

    with open(input_file, "r") as f:
        t20_contents = f.read()

    dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(expand_envvars = False, expand_user = False, allow_var_dupes = False, inherit_options = False, var_decorator = VAR_DECO))

    v, r = dsl.parse(t20_contents)
    if not v:
        return False, r

    v, r = dsl.get_all_sub_contexts()
    if not v:
        return False, r
    subctxs = r

    for ctx in subctxs:

        gen_contents += "\n\n// %s\n%s" % (ctx.get_name(), format_line_ctx(PREFIX, ctx, prod_ctx.get_counter()))

        v, r = dsl.get_all_variables(ctx.get_name())
        if not v:
            return False, r
        all_vars = r

        var_idx = 0
        for var in all_vars:
            gen_contents += "\n%s" % format_line_var(PREFIX, ctx, var, var_idx)
            var_idx += 1

    return True, gen_contents

def generate_header_index(input_files, output_file):

    header_guard_name = "GENERATED"

    generated_contents = ""
    generated_contents += "\n#ifndef _%s_H_\n#define _%s_H_" % (header_guard_name, header_guard_name)

    prod_ctx = ProdCtx()

    for current_t20 in input_files:

        if not os.path.exists(current_t20):
            return False, "[%s] does not exist." % current_t20

        v, r = gen_from_t20(current_t20, prod_ctx)
        if not v:
            return False, r

        generated_contents += r

    generated_contents += "\n\n#endif // _%s_H_\n" % header_guard_name

    with open(output_file, "w+") as f:
        f.write(generated_contents)

    return True, None

def puaq(selfhelp):
    print("Usage: %s output_file.h input1.t20 [input2.t20 ...]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    output_file = sys.argv[1]
    input_files = sys.argv[2:]

    v, r = generate_header_index(input_files, output_file)
    if not v:
        print(r)
        sys.exit(1)
