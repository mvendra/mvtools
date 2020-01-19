#!/usr/bin/env python3

TTY_WHITE = "\033[0m"
TTY_RED = "\033[31m"
TTY_GREEN = "\033[32m"
TTY_BLUE = "\033[94m"

def get_standard_color():
    return TTY_WHITE # mvtodo: eventually this should dynamically read the env - LS_COLORS, likely

if __name__ == "__main__":
    print("A script to retrieve the envionment's terminal colors.")

