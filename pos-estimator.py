#!/usr/bin/env python3
import json
import sys
import os
import math
import numpy as np
import operator

from threading import Thread

import pika

power_angle = {}
rf_angle = {}
rf_count = False
rssi_count = False

def calculate_distance(avg_power):
    ptx =  16 # router transmit power in dbm
    loss = ptx - avg_power # real detected power loss in dBm

    # Free Space Path loss model
    fspl_param = 92.5 + 7.6

    fspl_d = 10**((loss - fspl_param)/20) # estimate distance in km
    fspl_d_m = fspl_d * 1000 # estimate distance in meter

    ## Fit Equation from Calibration ##
    log_d = (avg_power+16.5)/(-17.77)
    d_m=10**log_d 
    return d_m,fspl_d_m

def estimate_coordinate(angle, distance):
    angle=0
    x = distance * math.sin(angle)
    y = distance * math.cos(angle)
    return x,y

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel1 = connection.channel()
    connection2 = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel2 = connection2.channel()

    #channel2.exchange_declare(exchange='rf_power', exchange_type='direct')
    channel1.exchange_declare(exchange='direct_power', exchange_type='direct')
    
    result1 = channel1.queue_declare(queue='', exclusive=True)
    result2 = channel2.queue_declare(queue='', exclusive=True)
    queue_name = result1.method.queue
    queue_name2 = result2.method.queue

    channel2.queue_bind(exchange='rf_power',
                queue=queue_name2,
                routing_key='rf-power-avg')

    channel1.queue_bind(exchange='direct_power',
                    queue=queue_name,
                    routing_key='Angle-power-avg')

    def rssi_callback(ch, method, properties, body):
        global power_angle
        global rssi_count

        message = json.loads(body)
        angle = message['Angle']
        avg_power = message['RSSI']
        power_angle[angle]=avg_power

        if rssi_count==True:
            beacon_angle = max(power_angle.items(), key=operator.itemgetter(1))[0]
            max_power = power_angle[beacon_angle]

            dist,fspl_dist = calculate_distance(max_power)
            x,y = estimate_coordinate(beacon_angle,dist)
            
            print('Angle : {}, RSSI Power : {}, FSPL Distance : {}'.format(beacon_angle,max_power,fspl_dist))
            print('Distance : {}'.format(dist))
            print('X : {}, Y:{}'.format(x,y))
        
        if angle==170:
            rssi_count = True
        else:
            rssi_count = False
    
    def rf_callback(ch, method, properties, body):
        global rf_angle
        global rf_count

        message = json.loads(body)
        angle = message['Angle']
        avg_power = message['RF Power']
        rf_angle[angle]=avg_power

        if rf_count==True:
            beacon_angle = max(rf_angle.items(), key=operator.itemgetter(1))[0]
            max_power = rf_angle[beacon_angle]

            dist,fspl_dist = calculate_distance(max_power)
            x,y = estimate_coordinate(beacon_angle,dist)
            
            print('Angle : {}, RF power : {}, FSPL Dist : {}'.format(beacon_angle,max_power,fspl_dist))
            print('Distance : {}'.format(dist))
            print('X : {}, Y:{}'.format(x,y))
        
        if angle==170:
            rf_count = True
        else:
            rf_count = False
            
    channel2.basic_consume(queue=queue_name2, on_message_callback=rf_callback, auto_ack=True)
    channel1.basic_consume(queue=queue_name, on_message_callback=rssi_callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    rssi_receiver = Thread(target=channel1.start_consuming)
    rf_receiver = Thread(target=channel2.start_consuming)
    rssi_receiver.start()
    rf_receiver.start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n \n Interrupted')
        print(power_angle)
        beacon_angle = max(power_angle.items(), key=operator.itemgetter(1))[0]
        max_power = power_angle[beacon_angle]
        print('Angle : {}, Max power : {}'.format(beacon_angle,max_power))
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)