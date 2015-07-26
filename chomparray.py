#!/usr/bin/env python

import sys

# chomparray.py
# sample usage:
# chomparray.py r1 aaa bbb ccc -> yields "aaa bbb"
# chomparray.py l1 aaa bbb ccc -> yields "bbb ccc"

bucket=[]
for args in sys.argv[2:]:
    bucket.append(args)

option=sys.argv[1]
d=option[0]
m=int(option[1:])

ret=None
if d=="l": # left
    ret=bucket[m:]
elif d=="r": # right
    ret=bucket[:len(bucket)-m]

toline=""
for p in ret:
    toline+=p+" "
toline=toline[:len(toline)-1] # removes trailing blank space
print(toline)

