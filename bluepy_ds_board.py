#!/usr/bin/env python
from bluepy.btle import *
import sys
from helper import *
import sys
import http.client, urllib
import logging as log

Address = 'DE:F7:1D:89:55:D5'

# Initializing logging info for the log file.
format = "%(asctime)s.%(msecs)03d: %(message)s"
log.basicConfig(format=format,
                    level = log.INFO,
                    datefmt="%H:%M:%S")


#   DS_UUID = 'e66e54fc-4231-41ae-9663-b43f50cfcb3b'
#   
#   CCCD_UUID = '2902'



def send_message(_msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a8q76apfdh5smhxg6k234yc1djzr8r",
        "user": "a32wsusbc7ouc64jfuhm8dgqi778js",
        "message": _msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()



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


class notifDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        dat=int.from_bytes(data, byteorder=sys.byteorder)
        if(cHandle == DS.ds_temp_chrcs[0].valHandle):
            DS.ds_temp_is_fresh[0]=True
            DS.ds_temp_datas[0] = (dat/100)
            print("DS temp1: {}".format(dat/100))
            if(all(DS.ds_temp_is_fresh)):
                DS.prepare_influx_data("Only_DS_Sensors")

        elif(cHandle == DS.ds_temp_chrcs[1].valHandle):
            DS.ds_temp_is_fresh[1]=True
            DS.ds_temp_datas[1] = (dat/100)
            print("DS temp2: {}".format(dat/100))
            if(all(DS.ds_temp_is_fresh)):
                DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS.ds_temp_chrcs[2].valHandle):
            DS.ds_temp_is_fresh[2]=True
            DS.ds_temp_datas[2] = (dat/100)
            print("DS temp3: {}".format(dat/100))
            if(all(DS.ds_temp_is_fresh)):
                DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS.ds_temp_chrcs[3].valHandle):
            DS.ds_temp_is_fresh[3]=True
            DS.ds_temp_datas[3] = (dat/100)
            print("DS temp4: {}".format(dat/100))
            if(all(DS.ds_temp_is_fresh)):
                DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS.ds_temp_chrcs[4].valHandle):
            DS.ds_temp_is_fresh[4]=True
            DS.ds_temp_datas[4] = (dat/100)
            print("DS temp5: {}".format(dat/100))
            if(all(DS.ds_temp_is_fresh)):
                DS.prepare_influx_data("Only_DS_Sensors")

    
counter=0
while(1):
    try:
        log.debug("Counter: {} Starting taking sensor data".format(counter))
        per = connect_device(Address)
        print_svcs(per)
        
        log.debug("Enabling ALL SENSORS...\n")

        DS = DS_service(periph=per, UUID='e66e54fc-4231-41ae-9663-b43f50cfcb3b', _num_sensors=5)
        
        
        log.debug("Configuring ALL SENSORS...\n")

        DS.configure()
        
        log.debug("Done Configuring sensors...\n")
        while True:
            if per.waitForNotifications(1.0):
                continue

    except Exception as e:
        per.disconnect()
        log.error("Exception: {}".format(e))
        send_message("Exception: {}".format(e))
        if counter == 15:
            quit()
        counter+=1
        time.sleep(10)
