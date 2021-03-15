import sys
import os
import time
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
line = connection.channel()

line.exchange_declare(exchange='beam-angle',
                    exchange_type='fanout')

while True:
    try:
        for i in range(0,190,10):
            data = i
            line.basic_publish(exchange='beam-angle',
                            routing_key='',
                            body=str(data))
            print(" {} Packet sent".format(data))
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)