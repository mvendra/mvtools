
# this was mousefix unnamed (1?)
xset m 0 0
xinput set-prop 10 265 -1 # the first number is the device. the second, Device Accel Profile, and the third, the value. see xinput --list and xinput --list-props DEVICE_ID

# this was mousefix2

xinput set-prop 10 279 -1
#xinput --list-props 10
#xinput set-prop 10 "Device Accel Constant Deceleration" 1.0

# this was mousefix3
xinput set-prop 8 "Device Accel Constant Deceleration" 1.5

# this was mousefix4

xinput --set-prop 8 "Device Accel Constant Deceleration" 1
xinput --set-prop 8 "Device Accel Adaptive Deceleration" 9

