#!/usr/bin/env python3
import sys
import os
import time

import pika
import serial

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
line = connection.channel()

line.exchange_declare(exchange='beam-angle',
                    exchange_type='fanout')

packet_update_period = 0.5 # in seconds

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()

    try:
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').rstrip()
                print(data)
                line.basic_publish(exchange='beam-angle',
                                routing_key='',
                                body=str(data))
                print(" {} Packet sent".format(data))
                
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)