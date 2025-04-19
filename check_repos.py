#!/usr/bin/env python3

import os
import sys

import path_utils
import fsquery
import mvtools_exception
import git_visitor_base
import git_lib
import terminal_colors
import mvtools_envvars

check_repos_options = {}

def check_template_example(repos, options):

    result = True
    for rp in repos:
        v, r = git_lib.get_remotes(rp)
        remotes = r
        for rmn in remotes:
            for rmop in remotes[rmn]:
                local_folder_name = os.path.basename(rp) # local folder name
                remote_path = remotes[rmn][rmop] # remote path
                remote_path_base_name = os.path.basename(remote_path) # remote path base name
                remote_path_base_name_no_git_folder = git_visitor_base.pluck_dotgit([remote_path_base_name])[0]

                print("rmn: %s " % rmn)
                print("rmop: %s " % rmop)
                print("local_folder_name: %s" % local_folder_name)
                print("remote_path: %s" % remote_path)
                print("remote_path_base_name: %s" % remote_path_base_name)
                print("remote_path_base_name_no_git_folder: %s" % remote_path_base_name_no_git_folder)
                # if error: print_error("reason") result = False

    return result

def print_success(msg):
    print("%s: %s%s%s" % (os.path.basename(__file__), terminal_colors.TTY_GREEN, msg, terminal_colors.get_standard_color()))

def print_error(msg):
    print("%s: %s%s%s" % (os.path.basename(__file__), terminal_colors.TTY_RED, msg, terminal_colors.get_standard_color()))

def filter_bare_git_repos(repos):

    repos_result = []

    for x in repos:
        v, r = git_lib.is_repo_bare(x)
        if not v:
            raise mvtools_exception.mvtools_exception(r)
        if r:
            repos_result.append(x)

    return repos_result

def sanitize_remote_path(path):
    if path is None:
        return None
    if path == "":
        return None
    if path[len(path)-1] == os.sep:
        return path[:len(path)-1]
    return path

def search_dupes(repo, repo_tuple_list):

    repo_bn = os.path.basename(repo)
    for rp in repo_tuple_list:
        if repo_bn == rp[0]:
            return True, rp[1]
    return False, ""

def no_duplicated_check(repos):

    if not check_repos_options["dupes-check"]:
        return True

    all_repos_tuple_list = []

    result = True
    for rp in repos:
        has_it, what_is_it = search_dupes(rp, all_repos_tuple_list)
        if has_it:
            print_error("%s and %s are duplicated." % (rp, what_is_it))
            result = False
        else:
            all_repos_tuple_list.append((os.path.basename(rp), rp))

    return result

def remotes_check(repos):

    if len(check_repos_options["offline-remotes-check"]) == 0 and len(check_repos_options["online-remotes-check"]) == 0:
        return True

    result = True
    for rp in repos:
        v, r = git_lib.get_remotes(rp)
        remotes = r
        local_basename = os.path.basename(rp)

        if remotes is None:
            print_error("%s has no remotes at all." % rp)
            result = False
            continue

        # check offline repos
        for opts_rem in check_repos_options["offline-remotes-check"]:

            if not opts_rem in remotes:
                print_error("%s has no %s offline-remote." % (rp, opts_rem))
                result = False

            if opts_rem in remotes:
                for ops in remotes[opts_rem]:

                    # every repo's offline remote should point to a local mount point (no https or git@)
                    if "https" in remotes[opts_rem][ops] or "git@" in remotes[opts_rem][ops]:
                        print_error("%s's offline-remote (%s) is not on a local mount point." % (rp, ops))
                        result = False

        # check online repos
        for opts_rem in check_repos_options["online-remotes-check"]:

            if not opts_rem in remotes:
                print_error("%s has no %s online-remote." % (rp, opts_rem))
                result = False

            if opts_rem in remotes:
                for ops in remotes[opts_rem]:

                    # every repo's online remote should point to an URL (https or git@)
                    if not "https" in remotes[opts_rem][ops] and not "git@" in remotes[opts_rem][ops]:
                        print_error("%s's online-remote (%s) is not an online URL." % (rp, ops))
                        result = False

    return result

def basenames_check(repos):

    if not check_repos_options["basenames-check"]:
        return True

    result = True
    for rp in repos:
        v, r = git_lib.get_remotes(rp)
        remotes = r
        local_basename = os.path.basename(rp)

        if remotes is None:
            print("Skipping basename check for %s because it has no remotes." % rp)
            continue

        for rnames in remotes:
            for rops in remotes[rnames]:
                rpath = remotes[rnames][rops]

                remote_basename = os.path.basename(sanitize_remote_path(rpath))
                if remote_basename.endswith(".git"):
                    remote_basename = remote_basename[0:len(remote_basename)-4]
                if remote_basename != local_basename:
                    print_error("%s's local and remote (%s, %s, %s) basenames are different." % (rp, rnames, remote_basename, rops))
                    result = False

    return result

def repo_storages_comparison_check(repos):

    if check_repos_options["compare-repo-storage"] is None:
        return True

    # get list of repos from other storage, to compare with local storage
    v, r = fsquery.makecontentlist(check_repos_options["compare-repo-storage"], True, False, False, True, False, True, True, [])
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    compare_repos = r

    compare_repos = filter_bare_git_repos(compare_repos)

    visitor_repos_len = len(repos)
    compare_repos_len = len(compare_repos)

    # most basic test - quantity of repos should be the same
    if visitor_repos_len != compare_repos_len:
        print_error("Repos from visitor and from [%s] have a different repo count: [%s] vs [%s]" % (check_repos_options["compare-repo-storage"], visitor_repos_len, compare_repos_len))
        return False

    v, r = mvtools_envvars.mvtools_envvar_read_git_visitor_base()
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    visitor_base_path = r

    # filter out the visitor base path out of the repos path
    repos_filtered = []
    for entry in repos:

        v, r = path_utils.based_path_find_outstanding_path(visitor_base_path, entry)
        if not v:
            raise mvtools_exception.mvtools_exception(r)
        entry_repos_outstanding = r

        repos_filtered.append(entry_repos_outstanding)

    result = True

    # check if they are all synchronized, filesystem-tree-wise
    for entry in compare_repos:

        v, r = path_utils.based_path_find_outstanding_path(check_repos_options["compare-repo-storage"], entry)
        if not v:
            raise mvtools_exception.mvtools_exception(r)
        entry_compare_outstanding = r

        if not entry_compare_outstanding in repos_filtered:
            print_error("Unable to find the equivalent of [%s] within the local storage" % entry)
            result = False

    return result

def visitor_check_repos(repos, options):

    all_results = []
    all_results.append(no_duplicated_check(repos))
    all_results.append(remotes_check(repos))
    all_results.append(basenames_check(repos))
    all_results.append(repo_storages_comparison_check(repos))

    if False in all_results:
        print_error("Not all tests passed.")
        return False
    print_success("All tests passed.")
    return True

def check_repos():

    r = git_visitor_base.do_visit(None, None, visitor_check_repos)
    if False in r:
        return False
    return True

if __name__ == "__main__":

    cmdline_options = sys.argv[1:]

    check_repos_options["compare-repo-storage"] = None
    check_repos_options["basenames-check"] = False
    check_repos_options["dupes-check"] = False
    check_repos_options["offline-remotes-check"] = []
    check_repos_options["online-remotes-check"] = []

    compare_repo_storage_parse_next = False
    offline_remotes_check_parse_next = False
    online_remotes_check_parse_next = False

    for p in cmdline_options:

        if compare_repo_storage_parse_next:
            check_repos_options["compare-repo-storage"] = p
            compare_repo_storage_parse_next = False
            continue

        if offline_remotes_check_parse_next:
            check_repos_options["offline-remotes-check"].append(p)
            offline_remotes_check_parse_next = False
            continue

        if online_remotes_check_parse_next:
            check_repos_options["online-remotes-check"].append(p)
            online_remotes_check_parse_next = False
            continue

        if p == "--compare-repo-storage":
            compare_repo_storage_parse_next = True
            continue

        if p == "--basenames-check":
            check_repos_options["basenames-check"] = True
            continue

        if p == "--dupes-check":
            check_repos_options["dupes-check"] = True
            continue

        if p == "--offline-remotes-check":
            offline_remotes_check_parse_next = True
            continue

        if p == "--online-remotes-check":
            online_remotes_check_parse_next = True
            continue

    check_repos()
