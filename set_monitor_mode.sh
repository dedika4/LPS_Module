#!/bin/bash
# A script to set device to monitor mode

WIRELESS_ADAPTER = 'wlan1'

airmon-ng start $WIRELESS_ADAPTER