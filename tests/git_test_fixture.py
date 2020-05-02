#!/usr/bin/env python3

import os
import path_utils
import create_and_write_file
import git_wrapper

def git_createAndCommit(repo, filename, content, commitmsg):

    file_final = path_utils.concat_path(repo, filename)
    if not create_and_write_file.create_file_contents(file_final, content):
        return False, "create_and_write_file command failed. Can't proceed. File: %s." % file_final

    v, r = git_wrapper.stage(repo)
    if not v:
        return v, r

    return git_wrapper.commit(repo, commitmsg)
