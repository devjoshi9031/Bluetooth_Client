#!/usr/bin/env python
# from Bluetooth_Client.helper import BMP_service, DS_service, LSM_service, SCD_service
from bluepy.btle import *
import sys
from helper import *
import time
import sys
import datetime
import urllib3

import http.client, urllib
import logging as log
from influxdb_helper import *
import urllib.request

def check_internet(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

# test
print( "connected" if connect() else "no internet!" )


Address = 'DE:F7:1D:89:55:D5'

def print_svcs(per):
        svc = per.getServices()
        for s in svc:
                ch = s.getCharacteristics()
                for c in ch:
                        print(s.uuid, c)

def connect_device(addr):
    print("Connecting to {} device...".format(addr))
    per = Peripheral(addr, ADDR_TYPE_RANDOM, iface=0)
    per.setDelegate(notifDelegate())
    print("Successfully Connected to {} device\n".format(addr))
    return per

#def check_services(svs):
#    if 

class notifDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        dat=int.from_bytes(data, byteorder=sys.byteorder)



# def internet_on():
#     try:
#         http = urllib3.PoolManager()
#         url = "www.google.com"
#         resp = http.request('GET', url)
#         return True
#     except urllib3.exceptions.MaxRetryError as err: 
#         print("Error Caught")
#         return False


while(1):
    try:
        per = connect_device(Address)
        print_svcs(per)
        print("Internet is: {}".format(connect()))
        while True:
            if per.waitForNotifications(1.0):
                continue
    except BTLEException as e:
        print(e)
