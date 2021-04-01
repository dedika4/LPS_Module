#!/usr/bin/env python3
import json
import sys
import os
import math
import operator

import pika

power_angle = {}

def calculate_distance(avg_power,path_loss_model='fspl'):
    ptx = 20 # router transmit power in dbm
    loss = ptx - avg_power # real detected power loss in dBm

    # Path loss model
    if path_loss_model =='fspl':
        loss_param = 92.5 + 7.6
    else:
        loss_param = 0

    d = 10**((loss - loss_param)/20) # estimate distance in km
    d_m = d * 1000 # estimate distance in meter
    return d_m

def estimate_coordinate(angle, distance):
    x = distance * math.sin(angle)
    y = distance * math.cos(angle)
    return x,y

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='direct_power', exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='direct_power',
                    queue=queue_name,
                    routing_key='Angle-power-avg')

    def callback(ch, method, properties, body):
        global power_angle

        message = json.loads(body)
        angle = message['Angle']
        avg_power = message['RSSI']

        power_angle[angle]=avg_power
        beacon_angle = max(power_angle.items(), key=operator.itemgetter(1))[0]
        max_power = power_angle[beacon_angle]

        dist = calculate_distance(beacon_angle,'fspl')
        x,y = estimate_coordinate(beacon_angle,dist)
        
        print('Angle : {}, Max power : {}'.format(beacon_angle,max_power))
        print('Distance : {}'.format(dist))
        print('X : {}, Y:{}'.format(x,y))

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        print(power_angle)
        beacon_angle = max(power_angle.items(), key=operator.itemgetter(1))[0]
        max_power = power_angle[beacon_angle]
        print('Angle : {}, Max power : {}'.format(beacon_angle,max_power))
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)