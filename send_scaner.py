#!/usr/bin/env python
import pika
from scapy.all import *
from threading import Thread
import pandas
import time
import os

# initialize connection to RabbitMQ Server 
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
line = connection.channel()

# initialize exchange and queue and bind them
line.exchange_declare(exchange='beam-angle', 
                    exchange_type='fanout')

result = line.queue_declare(queue='', 
                    exclusive=True)

queue_name = result.method.queue
line.queue_bind(exchange='beam-angle',
                queue=queue_name)

# initialize the networks dataframe that will contain all access points nearby
networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto"])
# set the index BSSID (MAC address of the AP)
networks.set_index("BSSID", inplace=True)

beacon_SSID = 'REPN'
beacon_found = False
beacon_channel = 11
channel_hoping = False

# interface name, check using iwconfig
interface = "wlan1mon"

data = []
angle = -1
count = 0
avg_power = 0

t = time.time()
packet_update_period = 0.5 # in seconds

def callback(packet):
    global data
    global angle
    global count
    global avg_power
    global t

    t_now = time.time()
    if (angle!=-1):
        if packet.haslayer(Dot11Beacon):
            # extract the MAC address of the network
            bssid = packet[Dot11].addr2
            # get the name of it
            ssid = packet[Dot11Elt].info.decode()
            try:
                dbm_signal = packet.dBm_AntSignal
            except:
                dbm_signal = "N/A"
            # extract network stats
            stats = packet[Dot11Beacon].network_stats()
            # get the channel of the AP
            channel = stats.get("channel")
            # get the crypto
            crypto = stats.get("crypto")
            networks.loc[bssid] = (ssid, dbm_signal, channel, crypto)
            if t_now - t < packet_update_period:
                if (ssid == beacon_SSID) and (dbm_signal != "N/A"):
                    avg_power += int(dbm_signal)
                    count +=1
                #print('Packet count : {}'.format(count))
                #print('Average Power : {}'.format(avg_power))
            else:
                print('Its time')
                if count!=0: 
                    avg_power = avg_power/count
                data = [angle, avg_power]
                print('Average power : {:.3f} for {} degree angle'.format(avg_power,angle))
                count = 0
                avg_power = 0
                t = time.time()

def print_all():
    global angle
    while True:
        #os.system("clear")
        #print(networks)
        #print(" [x] Packet sent")
        time.sleep(0.1)


def change_channel():
    ch = 1
    while True:
        os.system(f"iwconfig {interface} channel {ch}")
        # switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)

def receive_angle(ch, method, properties, body):
    global angle
    print('Angle : {}'.format(angle))
    angle = int(body)

# define consuming properties
line.basic_consume(queue=queue_name, 
                    on_message_callback=receive_angle, 
                    auto_ack=True)

def main():
    os.system(f"iwconfig {interface} channel {beacon_channel}")
    # start the thread that prints all the networks
    printer = Thread(target=print_all)
    printer.daemon = True
    printer.start()
    # start the channel changer
    if channel_hoping == True :
        channel_changer = Thread(target=change_channel)
        channel_changer.daemon = True
        channel_changer.start()
    # start receiving beam angle
    print('Waiting for angle ...')
    receiver = Thread(target=line.start_consuming)
    #receiver.daemon = True
    receiver.start()
    # start sniffing
    print('start sniffing')
    sniff(prn=callback, iface=interface)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)