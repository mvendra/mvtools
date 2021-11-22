#!/usr/bin/env python3

import sys
import os

import urllib.request

import path_utils

# credit: https://stackoverflow.com/questions/22676/how-to-download-a-file-over-http
def download_url(source_url, target_path):

    if os.path.exists(target_path):
        return False, "Target path [%s] already exists" % target_path

    contents = None
    try:
        with urllib.request.urlopen(source_url) as f:
            contents = f.read().decode("utf8")
    except urllib.error.HTTPError as httpex:
        return False, "Downloading failed: [%s]" % httpex

    with open(target_path, "w") as f:
        f.write(contents)

    return True, None

def puaq():
    print("Usage: %s source_url target_path" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    source_url = sys.argv[1]
    target_path = sys.argv[2]

    v, r = download_url(source_url, target_path)
    if not v:
        print(r)
        sys.exit(1)
