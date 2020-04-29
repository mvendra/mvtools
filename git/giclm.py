#!/usr/bin/env python3

""" GICLM
GIt Copy Last commit Message
Sends to the clipboard the last commit's message,
without the decorations.
"""

import os
import sys

import git_wrapper
import sendtoclipboard

def copy_last_commit_message(repo):

    v, r = git_wrapper.log(repo)
    if not v:
        print("copy_last_commit_message failed: %s" % r)
        sys.exit(1)

    msg = remove_gitlog_decorations(r)
    if msg is not None:
        sendtoclipboard.sendtoclipboard(msg)

def remove_gitlog_decorations(commitmsg):

    res = commitmsg

    # cut out first four lines (commit, author, date, \n)
    nl = -1
    for x in range(4):
        nl = res.find("\n", nl+1)
        if nl == -1:
            return None
    res = res[nl+1:]

    # remove the remaining commits
    remaining = res.find("\ncommit")
    if remaining != -1: # this could be the only commit. so we will only try to cut if there's more
        res = res[:remaining] 

    # remove the trailing last newline
    nl = res.rfind("\n")
    if nl == -1:
        return None
    res = res[:nl]

    # remove the indentation before each line
    res_lines = res.split("\n")
    res = ""
    for line in res_lines:
        line = line[4:]
        res += line + "\n"
    res = res[:len(res)-1] # the above code will always add a newline at the end of each line. this renders the last line "incorrect". lets fix it.

    return res

if __name__ == "__main__":

    repo_target = os.getcwd()
    if len(sys.argv) > 1:
        repo_target = sys.argv[1]
    copy_last_commit_message(repo_target)
