#!/usr/bin/env python3

""" GICLM
GIt Copy Last commit Message
Sends to the clipboard the last commit's message,
without the decorations.
"""

import os
import sys

import git_wrapper
import git_lib
import sendtoclipboard

def copy_last_commit_message(repo):

    v, r = git_wrapper.log(repo)
    if not v:
        print("copy_last_commit_message failed: %s" % r)
        sys.exit(1)

    msg = git_lib.remove_gitlog_decorations(r)
    if msg is not None:
        sendtoclipboard.sendtoclipboard(msg)

if __name__ == "__main__":

    repo_target = os.getcwd()
    if len(sys.argv) > 1:
        repo_target = sys.argv[1]
    copy_last_commit_message(repo_target)
