#!/usr/bin/env python
import pika
from scapy.all import *
from threading import Thread
import pandas
import time
import os

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
line = connection.channel()
line.queue_declare(queue='hello')

# initialize the networks dataframe that will contain all access points nearby
networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto"])
# set the index BSSID (MAC address of the AP)
networks.set_index("BSSID", inplace=True)

beacon_SSID = 'REPN'
beacon_found = False
beacon_channel = 2
channel_hoping = False

# interface name, check using iwconfig
interface = "wlan1mon"

data = []

def callback(packet):
    global data
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
        if ssid == beacon_SSID:
            data = ssid
        else:
            data = "no name bitch"

def print_all():
    while True:
        os.system("clear")
        print(networks)
        line.basic_publish(exchange='',
                      routing_key='hello',
                      body=data)
        print(" [x] Packet sent")
        time.sleep(0.1)


def change_channel():
    ch = 1
    while True:
        os.system(f"iwconfig {interface} channel {ch}")
        # switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)

if __name__ == "__main__":
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
    # start sniffing
    sniff(prn=callback, iface=interface)

connection.close()