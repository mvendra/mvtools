#!/usr/bin/env python3

import sys
import os

class mvtools_exception(BaseException):
    def __init__(self, _msg):
        self.message = _msg
    def get_message(self):
        return self.message
