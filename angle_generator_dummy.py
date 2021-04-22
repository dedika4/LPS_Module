import sys
import os
import time
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
line = connection.channel()

line.exchange_declare(exchange='beam-angle',
                    exchange_type='fanout')

packet_update_period = 0.5 #float(sys.argv[1]) # in seconds

while True:
    i = 0
    try:
        t = time.time()
        while i <= 180:
            t_now = time.time()
            if (t_now - t)>= packet_update_period:
                data = i
                line.basic_publish(exchange='beam-angle',
                                routing_key='',
                                body=str(data))
                print(" {} Packet sent".format(data))
                #time.sleep(0.5)
                i += 10
                t = time.time()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)