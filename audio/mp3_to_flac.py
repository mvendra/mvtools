#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def puaq():
    print("Usage: %s input_file.mp3" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def convert_mp3_to_flac(input_file, output_file, bitrate):
    cmd = ["ffmpeg", "-i", input_file, "-ab", bitrate, "-map_metadata", "0", "-id3v2_version", "3", output_file]
    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        print("Failed to convert file from mp3 to flac : %s" % r)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    input_file = sys.argv[1]
    output_file = ""

    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        output_file = (input_file.rsplit(".", 1)[0]) + ".flac"

    bitrate = "192k"

    convert_mp3_to_flac(input_file, output_file, bitrate)
