#!/bin/bash
# A script to execute local positioning feature

INTERVAL=$1
CHANNEL=$2

#python3 receiver.py
xterm -hold -e python3 pos-estimator.py &
xterm -hold -e python3 send_scaner.py $CHANNEL $INTERVAL&
xterm -hold -e python3 angle_generator_dummy.py $INTERVAL