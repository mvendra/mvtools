#!/usr/bin/env python

import datetime
import time

def get_timestamp_now():
    return datetime.datetime.fromtimestamp(time.time()).strftime("%d/%m/%Y - %H:%M:%S")

def get_timestamp_now_compact():
    return datetime.datetime.fromtimestamp(time.time()).strftime("%d%m%Y_%H%M%S")

if __name__ == "__main__":
    print(get_timestamp_now_compact())
