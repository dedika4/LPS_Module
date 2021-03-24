#!/usr/bin/env python3
import json
import sys
import os

import pika

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
        message = json.loads(body)
        print("At angle {} the average power is {}".format(message['Angle'],message['RSSI']))
        print(" [x] Received %r" % json.loads(body))

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