#!/usr/bin/env python3

import sys
import os

import path_utils
import terminal_colors

def is_digit(character):
    return character in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def is_hex_digit(character):
    return character in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

def scan_hex_address(line, check_trail):

    local_line = line

    if len(local_line) < 3:
        return False, "Unable to scan hex address: input line [%s] is smaller than 3" % line

    if local_line[0:2] != "0x":
        return False, "Unable to scan hex address: input line [%s] does not begin with hex prefix 0x" % line
    local_line = local_line[2:]

    idx = 0
    for c in local_line:
        if c == " ":
            break
        if not is_hex_digit(c):
            return False, "Unable to scan hex address: input line [%s] has invalid hex digit: [%s]" % (line, c)
        idx += 1

    if idx == 0:
        return False, "Unable to scan hex address: input line [%s] has no address" % line
    local_line = local_line[idx:]

    if idx > 16:
        return False, "Unable to scan hex address: input line [%s] has a too-large address" % line

    if check_trail:
        if len(local_line) < 2:
            return False, "Unable to scan hex address: input line [%s] has no trailing space" % line

        if local_line[0] != " ":
            return False, "Unable to scan hex address: input line [%s] has a valid address but no trailing space" % line
        local_line = local_line[1:]

        if len(local_line) < 1:
            return False, "Unable to scan hex address: input line [%s] has a valid address and trailing space, but nothing else" % line

        if local_line[0] == " ":
            local_line = local_line[1:]

    return True, local_line

def scan_next_frame_num(expected, line):

    local_line = line

    pos = local_line.find(" ")
    if pos == -1:
        return False, "Unable to scan next frame: input line [%s] has no spaces" % line
    cur_frame = local_line[0:pos]
    local_line = (local_line[pos:]).lstrip()

    if cur_frame.strip() == "":
        return False, "Unable to scan next frame: input line [%s] has space but nothing else" % line
    cur_frame = int(cur_frame)

    if cur_frame != expected:
        return False, "Unable to scan next frame: input line [%s] does not have the expected frame index: [%d]" % (line, expected)

    return True, local_line

def scan_eq_eq_pid_eq_eq(line):

    local_line = line

    if len(local_line) < 5:
        return False, None

    if local_line[0:2] != "==":
        return False, None
    local_line = local_line[2:]

    next_eq = local_line.find("=")
    if next_eq == -1:
        return False, None

    pid_entry = local_line[0:next_eq]
    for c in pid_entry:
        if not is_digit(c):
            return False, None
    local_line = local_line[next_eq:]

    if local_line[0:2] != "==":
        return False, None
    local_line = local_line[2:]

    return True, local_line

def is_asan_stack_entry(expected, line):

    local_line = line

    if len(local_line) < 5:
        return False, "Unable to detect stack entry: input line [%s] does not have a valid length" % line

    if local_line[0:5] != "    #":
        return False, "Unable to detect stack entry: input line [%s] does not have a valid prefix" % line
    local_line = local_line[5:]

    v, r = scan_next_frame_num(expected, local_line)
    if not v:
        return False, r
    local_line = r

    v, r = scan_hex_address(local_line, True)
    if not v:
        return False, r
    local_line = r

    if len(local_line) < 3:
        return False, "Unable to detect stack entry: input line [%s] does not have a valid length (after scanning hex address)" % line

    if local_line[0:3] == "in ":
        return True, None

    if len(local_line) >= 9:
        if local_line[0:9] == "([stack]+":
            return True, None

    if len(local_line) >= 18:
        if local_line == "(<unknown module>)":
            return True, None

    if len(local_line) >= 6:
        if local_line[0] == "(":
            plus_pos = local_line.find("+")
            if plus_pos != -1:
                this_addr = local_line[plus_pos:]
                if len(this_addr) > 1:
                    this_addr = this_addr[1:]
                    if this_addr[len(this_addr)-1] == ")":
                        this_addr = this_addr[:len(this_addr)-1]
                        this_addr += "  "
                        v, r = scan_hex_address(this_addr, True)
                        if not v:
                            return False, r
                        return True, None

    return False, "Unable to detect stack entry: input line [%s] is unrecognized" % line

def is_line_error_asan_segv_unk_addr(line):

    local_line = line

    v, r = scan_eq_eq_pid_eq_eq(local_line)
    if not v:
        return False
    local_line = r

    if len(local_line) < 49:
        return False

    if local_line[0:49] == "ERROR: AddressSanitizer: SEGV on unknown address ":
        return True

    return False

def is_line_sig_caused_by_read_or_write_mem_acc(line):

    local_line = line

    v, r = scan_eq_eq_pid_eq_eq(local_line)
    if not v:
        return False
    local_line = r

    if len(local_line) < 45:
        return False

    if local_line[0:45] == "The signal is caused by a READ memory access.":
        return True

    if len(local_line) < 46:
        return False

    if local_line[0:46] == "The signal is caused by a WRITE memory access.":
        return True

    return False

def is_line_hint_addr_point_zero_page(line):

    local_line = line

    v, r = scan_eq_eq_pid_eq_eq(local_line)
    if not v:
        return False
    local_line = r

    if len(local_line) < 38:
        return False

    if local_line[0:38] == "Hint: address points to the zero page.":
        return True

    return False

def is_line_aborting(line):

    local_line = line

    v, r = scan_eq_eq_pid_eq_eq(local_line)
    if not v:
        return False
    local_line = r

    if len(local_line) < 8:
        return False

    if local_line[0:8] == "ABORTING":
        return True

    return False

def asan_vga_v1_should_ignore_stack(stack_entries):

    ign_entries = ["(<unknown module>)", "_XimOpenIM", "nvidia_drv"]

    for sen in stack_entries:
        for ignen in ign_entries:
            if ignen in sen:
                return True

    if len(stack_entries) == 3:

        local_line = stack_entries[2]
        if len(local_line) < 5:
            return False

        if local_line[0:5] != "    #":
            return False
        local_line = local_line[5:]

        v, r = scan_next_frame_num(1, local_line)
        if not v:
            return False
        local_line = r

        v, r = scan_hex_address(local_line, True)
        if not v:
            return False
        local_line = r

        if len(local_line) < 2:
            return False

        if not ((local_line[0] == "(") and (local_line[len(local_line)-1] == ")")):
            return False
        local_line = local_line[1:len(local_line)-1]

        if len(local_line) < 6: # smallest valid combo I could think of at this point: /a+0x1 (binary/app named "a" inside the linux root folder, had a memory issue at address 0x1)
            return False

        pos = local_line.rfind("+")
        if pos == -1:
            return False
        app_path = local_line[0:pos]
        local_line = local_line[pos+1:]

        v, r = scan_hex_address(local_line, False)
        if not v:
            return False
        local_line = r

        if os.path.exists(app_path):
            return True

    return False

def filter_asan_echo(contents):

    contents_list = contents.split("\n")
    contents_list_result = ""

    n = 0
    exp_idx = 0
    stack_mode = False
    for l in contents_list:
        n += 1

        if stack_mode:

            if l == "":
                contents_list_result += "\n"
                exp_idx = 0
                stack_mode = False
                continue

            v, r = is_asan_stack_entry(exp_idx, l)
            if not v:
                return False, r
            exp_idx += 1

            contents_list_result += "%s\n" % l

        else:

            if l == "":
                if n != len(contents_list):
                    contents_list_result += "\n"
                continue

            if "=================================================================" == l:
                contents_list_result += "%s\n" % l
            elif "AddressSanitizer:DEADLYSIGNAL" == l:
                contents_list_result += "%s\n" % l
            elif is_line_error_asan_segv_unk_addr(l):
                contents_list_result += "%s%s%s\n" % (terminal_colors.TTY_RED_BOLD, l, terminal_colors.TTY_WHITE)
            elif is_line_sig_caused_by_read_or_write_mem_acc(l):
                contents_list_result += "%s\n" % l
            elif is_line_hint_addr_point_zero_page(l):
                contents_list_result += "%s\n" % l
                exp_idx = 0
                stack_mode = True
            elif "ERROR: LeakSanitizer: detected memory leaks" in l:
                contents_list_result += "%s%s%s\n" % (terminal_colors.TTY_RED_BOLD, l, terminal_colors.TTY_WHITE)
            elif "Direct leak of" in l or "Indirect leak of" in l:
                contents_list_result += "%s%s%s\n" % (terminal_colors.TTY_BLUE_BOLD, l, terminal_colors.TTY_WHITE)
                exp_idx = 0
                stack_mode = True
            elif "SUMMARY: AddressSanitizer:" in l:
                contents_list_result += "%s" % l
            elif "AddressSanitizer can not provide additional info." == l:
                contents_list_result += "%s\n" % l
            elif is_line_aborting(l):
                contents_list_result += "\n%s" % l
            else:
                return False, "Unable to detect pattern: [%s] (line number %d)" % (l, n-1)

    return True, contents_list_result

def filter_asan_vga_v1(contents):

    contents_list = contents.split("\n")
    contents_list_result = ""

    exp_idx = 0
    stack_mode = False
    stack_entry = []
    n = 0
    for l in contents_list:
        n += 1

        if stack_mode:

            if l == "":
                exp_idx = 0
                stack_mode = False
                if not asan_vga_v1_should_ignore_stack(stack_entry):
                    for sen in stack_entry:
                        contents_list_result += "%s\n" % sen
                    contents_list_result += "\n"
                stack_entry = []
                continue

            v, r = is_asan_stack_entry(exp_idx, l)
            if not v:
                return False, r
            exp_idx += 1

            stack_entry.append(l)

        else:

            if l == "":
                if n != len(contents_list):
                    contents_list_result += "\n"
                continue

            if "Direct leak of" in l or "Indirect leak of" in l:
                exp_idx = 0
                stack_mode = True
                stack_entry = []
                stack_entry.append(l)
                continue

            contents_list_result += l
            if n != len(contents_list):
                contents_list_result += "\n"

    return True, contents_list_result

def apply_filters(contents, asan_echo, asan_vga_v1):

    local_contents = contents

    if asan_vga_v1:
        v, r = filter_asan_vga_v1(local_contents)
        if not v:
            return False, r
        local_contents = r

    if asan_echo: # asan_echo must be last of the asan filters
        v, r = filter_asan_echo(local_contents)
        if not v:
            return False, r
        local_contents = r

    return True, local_contents

def puaq():
    print("Usage: %s input_file [--asan-vga-v1 --asan-echo]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print("[%s] does not exist" % input_file)
        sys.exit(1)

    # filters
    asan_echo = False
    asan_vga_v1 = False

    for p in sys.argv[2:]:

        if p == "--asan-echo":
            asan_echo = True
        elif p == "--asan-vga-v1":
            asan_vga_v1 = True
        else:
            print("Unknown parameter: [%s]" % p)
            sys.exit(1)

    contents = ""
    with open(input_file, "r") as f:
        contents = f.read()

    v, r = apply_filters(contents, asan_echo, asan_vga_v1)
    print(r)

    if not v:
        sys.exit(1)
