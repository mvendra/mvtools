#!/usr/bin/env python

from subprocess import call

if __name__ == "__main__":

    name = raw_input("Input your name.\n")
    email = raw_input("Input your email.\n")

    call(["git", "config", "--global", "user.name", name])
    call(["git", "config", "--global", "user.email", email])

    call(["git", "config", "--global", "diff.tool", "meld"])
    call(["git", "config", "--global", "diff.external", "meldiff.py"])
    call(["git", "config", "--global", "push.default", "simple"])

