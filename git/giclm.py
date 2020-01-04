#!/usr/bin/env python3

""" GICLM
GIt Copy Last commit Message
Sends to the clipboard the last commit's message,
without the decorations.
"""

from subprocess import check_output
from subprocess import CalledProcessError

import sendtoclipboard

def copy_last_commit_message():
    try:
        out = check_output(["git", "log"])
    except CalledProcessError as cpe:
        print("Call to git log returned error.")
        exit(1)
    except OSError as oe:
        print("Call to git failed. Make sure it is installed.")
        exit(1)
    msg = remove_gitlog_decorations(out.decode("ascii"))
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
    copy_last_commit_message()

