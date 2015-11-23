#!/usr/bin/env python

""" GICLM
GIt Copy Last commit Message
Sends to the clipboard the last commit's message,
without the decorations.
"""

from subprocess import check_output

import sendtoclipboard

def copy_last_commit_message():
    out = check_output(["git", "log"])
    msg = remove_gitlog_decorations(out)
    if msg is not None:
        sendtoclipboard.sendtoclipboard(msg)

def remove_gitlog_decorations(commitmsg):

    res = commitmsg

    # cut out first four lines (commit, author, date, \n)
    nl = -1
    for x in xrange(4):
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
    copy_last_commit_message()

