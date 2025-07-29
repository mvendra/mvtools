#!/usr/bin/env python3

import sys
import os

import path_utils
import ffmpeg_wrapper

def puaq(selfhelp):
    print("Usage: %s input_file.flac" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

def convert_flac_to_mp3(input_file, output_file, bitrate):

    v, r = ffmpeg_wrapper.convert(input_file, output_file, bitrate)
    if not v:
        print("Failed to convert file from flac to mp3: [%s]" % r)
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    input_file = sys.argv[1]
    output_file = ""

    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        output_file = (input_file.rsplit(".", 1)[0]) + ".mp3"

    bitrate = "192k"

    convert_flac_to_mp3(input_file, output_file, bitrate)
