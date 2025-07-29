#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def convert(input_filename, output_filename, bitrate):

    input_filename_filtered = path_utils.filter_remove_trailing_sep(input_filename)
    output_filename_filtered = path_utils.filter_remove_trailing_sep(output_filename)

    if not os.path.exists(input_filename_filtered):
        return False, "Input filename [%s] does not exist." % input_filename_filtered

    if os.path.exists(output_filename_filtered):
        return False, "Output filename [%s] already exists." % output_filename_filtered

    full_cmd = ["ffmpeg", "-i", input_filename_filtered, "-ab", bitrate, "-map_metadata", "0", "-id3v2_version", "3", output_filename_filtered]
    v, r = generic_run.run_cmd_simple(full_cmd)
    if not v:
        return False, "Failed running ffmpeg convert command: [%s]" % r

    return True, None

def puaq(selfhelp):
    print("Usage: %s input_filename output_filename" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    v, r = convert(input_filename, output_filename, "192k")
    if not v:
        print(r)
        sys.exit(1)
