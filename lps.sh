#!/bin/bash
# A script to execute local positioning feature

#python3 receiver.py
xterm -hold -e python3 pos-estimator.py &
xterm -hold -e python3 send_scaner.py &
xterm -hold -e python3 angle_generator_dummy.py