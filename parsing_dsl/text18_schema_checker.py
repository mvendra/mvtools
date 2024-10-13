#!/usr/bin/env python3

import sys
import os

import path_utils
import dsl_type20

VAR_DECO = "* "

def compare_t18_schemas_delegate(left_filename, left_dsl, right_filename, right_dsl):

    report = []

    v, r = left_dsl.get_all_sub_contexts()
    if not v:
        return False, r
    left_subctxs = r

    v, r = right_dsl.get_all_sub_contexts()
    if not v:
        return False, r
    right_subctxs = r

    if len(left_subctxs) != len(right_subctxs):
        report.append("[%s] has [%d] groups, whereas [%s] has [%d]" % (left_filename, len(left_subctxs), right_filename, len(right_subctxs)))
        return True, report

    for i in range(len(left_subctxs)):

        left_cur_ctx = left_subctxs[i].get_name()
        right_cur_ctx = right_subctxs[i].get_name()

        if left_cur_ctx != right_cur_ctx:
            report.append("Groups at index [%d] are different: [%s][%s] vs. [%s][%s]" % (i, left_filename, left_cur_ctx, right_filename, right_cur_ctx))

        v, r = left_dsl.get_all_variables(left_cur_ctx)
        if not v:
            return False, r
        left_all_vars = r

        v, r = right_dsl.get_all_variables(right_cur_ctx)
        if not v:
            return False, r
        right_all_vars = r

        if len(left_all_vars) != len(right_all_vars):
            report.append("[%s][%s] has [%d] entries, whereas [%s][%s] has [%d]" % (left_filename, left_cur_ctx, len(left_all_vars), right_filename, right_cur_ctx, len(right_all_vars)))
            return True, report

        for j in range(len(left_all_vars)):

            left_cur_ctx_var = left_all_vars[j].get_name()
            right_cur_ctx_var = right_all_vars[j].get_name()

            if left_cur_ctx_var != right_cur_ctx_var:
                report.append("Entries at index [%d] (from groups at index [%d]) are different: [%s][%s][%s] vs. [%s][%s][%s]" % (j, i, left_filename, left_cur_ctx, left_cur_ctx_var, right_filename, right_cur_ctx, right_cur_ctx_var))

    return True, report

def compare_t18_schemas(left_t20, right_t20):

    if not os.path.exists(left_t20):
        return False, "[%s] does not exist." % left_t20

    if not os.path.exists(right_t20):
        return False, "[%s] does not exist." % right_t20

    left_dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(expand_envvars = False, expand_user = False, allow_var_dupes = False, inherit_options = False, var_decorator = VAR_DECO))
    right_dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(expand_envvars = False, expand_user = False, allow_var_dupes = False, inherit_options = False, var_decorator = VAR_DECO))

    t20_contents = ""
    with open(left_t20, "r") as f:
        t20_contents = f.read()

    v, r = left_dsl.parse(t20_contents)
    if not v:
        return False, r

    t20_contents = ""
    with open(right_t20, "r") as f:
        t20_contents = f.read()

    v, r = right_dsl.parse(t20_contents)
    if not v:
        return False, r

    v, r = compare_t18_schemas_delegate(path_utils.basename_filtered(left_t20), left_dsl, path_utils.basename_filtered(right_t20), right_dsl)
    return v, r

def puaq():
    print("Usage: %s left.t20 right.t20" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) != 3:
        puaq()

    left_t20 = sys.argv[1]
    right_t20 = sys.argv[2]

    v, r = compare_t18_schemas(left_t20, right_t20)
    if not v:
        print(r)
        sys.exit(1)

    if len(r) == 0:
        print("The T18 schemas of files [%s] and [%s] match." % (left_t20, right_t20))
    else:
        for i in r:
            print(i)
        sys.exit(1)
