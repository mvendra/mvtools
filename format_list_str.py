#!/usr/bin/env python3

import sys
import os

def format_list_str(input_list, separator):

    if input_list is None:
        return None

    out_msg = ""

    for i in range(len(input_list)):
        out_msg += input_list[i]
        if i < (len(input_list)-1):
            out_msg += separator

    return out_msg
