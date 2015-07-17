xset m 0 0

# mvtodo: detect and run for multiple mouses?

# xinput --list (and find the mouse device)
DEVICE_ID=("`xinput --list | grep -i mouse | parseid.py`")

# xinput --list-props DEVICE_ID (and find Device Accel Profile)
DEVICE_ACCEL_PROFILE=265

echo "mvtodo: automate DEVICE_ACCEL_PROFILE detection: $DEVICE_ACCEL_PROFILE $DEVICE"

xinput set-prop $DEVICE_ID $DEVICE_ACCEL_PROFILE -1

