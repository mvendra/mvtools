xset m 0 0

# xinput --list (and find the mouse device)
DEVICE_ID=10

# xinput --list-props DEVICE_ID (and find Device Accel Profile)
DEVICE_ACCEL_PROFILE=265

xinput set-prop $DEVICE_ID $DEVICE_ACCEL_PROFILE -1

