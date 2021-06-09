#!/usr/bin/env python
import time
import sys
import os
import json

import pika
import pandas
from scapy.all import *
from threading import Thread

import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# initialize connection to RabbitMQ Server 
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
line = connection.channel()
connection2 = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
line2 = connection2.channel()

# initialize exchange and queue and bind them
line.exchange_declare(exchange='beam-angle', 
                    exchange_type='fanout')
line2.exchange_declare(exchange='rf_power', 
                        exchange_type='direct')

result = line.queue_declare(queue='', 
                    exclusive=True)

queue_name = result.method.queue
line.queue_bind(exchange='beam-angle',
                queue=queue_name)

routing_key = 'rf-power-avg'

angle = -1
count = 0
rf_power_avg = 0

t = time.time()
packet_update_period = float(sys.argv[1]) # in seconds

def send_rf_power(message):
    print(" [x] Message sent")
    line2.basic_publish(exchange='rf_power', 
                        routing_key=routing_key, 
                        body=message)

def callback():
    print('start processing')
    global angle
    global t
    global rf_power_avg
    global count

    while True:
        t_now = time.time()
        if (angle!=-1):
            # The read_adc function will get the value of the specified channel (0-7).
            value = mcp.read_adc(0) #channel 0
            voltage = (value/1023)*3.3 #volt
            rf_power = (voltage-0.3857)/(-0.01979)
            if t_now - t < packet_update_period:
                rf_power_avg += float(rf_power)
                count +=1
            else:
                if count!=0: 
                    rf_power_avg = rf_power_avg/count
                data = {'Angle':angle, 'RF Power':rf_power_avg,'time':t_now-t}
                message = json.dumps(data,indent=2)
                print(message)
                send_rf_power(message)
                count = 0
                rf_power_avg = 0
                t = time.time()

def receive_angle(ch, method, properties, body):
    global angle
    angle = int(body)
    #print('Angle : {}'.format(angle))

# define consuming properties
line.basic_consume(queue=queue_name, 
                    on_message_callback=receive_angle, 
                    auto_ack=True)

def main():
    # start receiving beam angle
    print('Waiting for angle ...')
    receiver = Thread(target=line.start_consuming)
    #receiver.daemon = True
    receiver.start()
    print('Reading RF Power')
    detector = Thread(target=callback)
    detector.start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)