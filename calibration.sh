#!/bin/bash
# A script to execute calibration data gathering

DISTANCE=$1
INTERVAL=$2
CHANNEL=$3

echo 'Calibrating at distance ' $DISTANCE ' meter with ' $INTERVAL ' update time at channel ' $CHANNEL

xterm -hold -e python3 calibration_receiver.py $DISTANCE $INTERVAL &
sleep 1s
xterm -hold -e python3 send_scaner.py $CHANNEL $INTERVAL &
sleep 2s
xterm -hold -e python3 angle_generator_dummy.py $INTERVAL