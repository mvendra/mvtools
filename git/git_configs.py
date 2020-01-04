#!/usr/bin/env python3

from subprocess import call

def set_git_configs(name, email):

    call(["git", "config", "--global", "user.name", name])
    call(["git", "config", "--global", "user.email", email])

    call(["git", "config", "--global", "diff.tool", "meld"])
    call(["git", "config", "--global", "diff.external", "meldiff.py"])
    call(["git", "config", "--global", "push.default", "simple"])

if __name__ == "__main__":

    name = input("Input your name.\n")
    email = input("Input your email.\n")
    set_git_configs(name, email)
