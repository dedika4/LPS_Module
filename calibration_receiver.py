#!/usr/bin/env python3
import json
import sys
import os
import csv
import time

from threading import Thread

import pika

calib_dist = sys.argv[1]
packet_update_period = float(sys.argv[2]) # in seconds
timestamp = 0

FILE_NAME = 'power_at_'+str(calib_dist)+'m.csv'
FIELD_NAMES = ['rssi','rf power']
DURATION = 60 #in seconds

RSSI = 0
RF_Power = 0

t = time.time()
with open(FILE_NAME, mode='w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
    writer.writeheader()

def main():
    rssi_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    rssi_channel = rssi_connection.channel()
    rf_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    rf_channel = rf_connection.channel()

    rssi_channel.exchange_declare(exchange='direct_power', exchange_type='direct')
    rf_channel.exchange_declare(exchange='rf_power', exchange_type='direct')

    rssi_result = rssi_channel.queue_declare(queue='', exclusive=True)
    rssi_queue_name = rssi_result.method.queue
    rf_result = rf_channel.queue_declare(queue='', exclusive=True)
    rf_queue_name = rf_result.method.queue

    rssi_channel.queue_bind(exchange='direct_power',
                    queue=rssi_queue_name,
                    routing_key='Angle-power-avg')
    
    rf_channel.queue_bind(exchange='rf_power',
                queue=rf_queue_name,
                routing_key='rf-power-avg')

    def rssi_callback(ch, method, properties, body):
        global timestamp, FILE_NAME, FIELD_NAMES,RSSI
        timestamp+=packet_update_period

        if timestamp > DURATION:
            raise Exception("Data Gathering Done!")
    
        message = json.loads(body)
        #print("At angle {} the average power is {}".format(message['Angle'],message['RSSI']))
        print("Time : {}".format(timestamp))
        print(" [x] Received %r" % json.loads(body))
        RSSI = message['RSSI']

        #with open(FILE_NAME, mode='a') as csv_file:
        #    writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
         #   writer.writerow({'timestamp': timestamp, 'rssi': message['RSSI']})
    
    def rf_callback(ch, method, properties, body):
        global timestamp, FILE_NAME, FIELD_NAMES, RF_Power
        timestamp+=packet_update_period

        if timestamp > DURATION:
            raise Exception("Data Gathering Done!")

        message = json.loads(body)
        #print("At angle {} the average power is {}".format(message['Angle'],message['RSSI']))
        print("Time : {}".format(timestamp))
        print(" [x] Received %r" % json.loads(body))
        RF_Power = message['RF Power']

        #with open(FILE_NAME, mode='a') as csv_file:
         #   writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
        #    writer.writerow({'timestamp': timestamp, 'rf power': message['RF Power']})
    
    def write_to_file():
        global timestamp,t,FILE_NAME, FIELD_NAMES,RSSI,RF_Power
        while True:
            t_now = time.time()
            if t_now - t > packet_update_period:
                with open(FILE_NAME, mode='a') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
                    writer.writerow({'rssi': RSSI,'rf power': RF_Power})
                t = time.time()

    rssi_channel.basic_consume(queue=rssi_queue_name, on_message_callback=rssi_callback, auto_ack=True)
    rf_channel.basic_consume(queue=rf_queue_name, on_message_callback=rf_callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    rssi_receiver = Thread(target=rssi_channel.start_consuming)
    rf_receiver = Thread(target=rf_channel.start_consuming)
    writer = Thread(target=write_to_file)
    rssi_receiver.start()
    rf_receiver.start()
    writer.start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)