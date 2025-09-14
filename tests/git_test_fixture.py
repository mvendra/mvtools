#!/usr/bin/env python

import os
import path_utils
import create_and_write_file
import git_wrapper

def git_createAndCommit(repo, filename, content, commitmsg):

    file_final = path_utils.concat_path(repo, filename)
    create_and_write_file.create_file_contents(file_final, content)

    v, r = git_wrapper.stage(repo, [file_final])
    if not v:
        return v, r

    return git_wrapper.commit(repo, commitmsg)
