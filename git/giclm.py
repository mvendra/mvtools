#!/usr/bin/env python

""" GICLM
GIt Copy Last commit Message
Sends to the clipboard the last commit's message,
without the decorations.
"""

import os
import sys

import git_lib
import sendtoclipboard

def copy_last_commit_message(repo):

    v, r = git_lib.log(repo)
    if not v:
        print("copy_last_commit_message failed: %s" % r)
        sys.exit(1)

    msg = git_lib.remove_gitlog_decorations(r)
    if msg is not None:
        v, r = sendtoclipboard.sendtoclipboard(msg)
        if not v:
            print(r)
            sys.exit(1)

if __name__ == "__main__":

    repo_target = os.getcwd()
    if len(sys.argv) > 1:
        repo_target = sys.argv[1]
    copy_last_commit_message(repo_target)
