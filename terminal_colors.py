#!/usr/bin/env python3

TTY_WHITE = "\033[0m"
TTY_WHITE_BOLD = "\033[01m"
TTY_WHITE_ITALIC = "\033[03m"
TTY_WHITE_BLINK = "\033[05m"
TTY_WHITE_STRIKETHRU = "\033[09m"

TTY_DARK_YELLOW = "\033[33m"
TTY_YELLOW = "\033[93m"
TTY_YELLOW_BOLD = "\033[1;33m"

TTY_LIGHT_RED = "\033[91m"
TTY_RED = "\033[31m"
TTY_RED_BOLD = "\033[1;31m"

TTY_LIGHT_GREEN = "\033[92m"
TTY_GREEN = "\033[32m"
TTY_GREEN_BOLD = "\033[1;32m"

TTY_BLUE = "\033[94m"
TTY_BLUE_BOLD = "\033[1;34m"
TTY_PURPLE = "\033[35m"

TTY_LIGHT_GRAY = "\033[02m"
TTY_DARK_GRAY = "\033[90m"
TTY_CYAN = "\033[96m"

def get_standard_color():
    return TTY_WHITE # mvtodo: eventually this should dynamically read the env - LS_COLORS, likely

if __name__ == "__main__":
    print("A script to retrieve the envionment's terminal colors.")

