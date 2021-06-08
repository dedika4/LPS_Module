#!/usr/bin/env python3
import json
import sys
import os
import csv

import pika

calib_dist = sys.argv[1]
packet_update_period = float(sys.argv[2]) # in seconds
timestamp = 0

FILE_NAME = 'power_at_'+str(calib_dist)+'m.csv'
FIELD_NAMES = ['timestamp', 'rssi']
DURATION = 300 #in seconds

with open(FILE_NAME, mode='w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
    writer.writeheader()

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
        global timestamp, FILE_NAME, FIELD_NAMES
        timestamp+=packet_update_period

        if timestamp > 180:
            raise Exception("Data Gathering Done!")
    
        message = json.loads(body)
        #print("At angle {} the average power is {}".format(message['Angle'],message['RSSI']))
        print("Time : {}".format(timestamp))
        print(" [x] Received %r" % json.loads(body))

        with open(FILE_NAME, mode='a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
            writer.writerow({'timestamp': timestamp, 'rssi': message['RSSI']})

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)