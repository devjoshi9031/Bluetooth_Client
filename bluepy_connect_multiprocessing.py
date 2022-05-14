#!/usr/bin/env python
# from Bluetooth_Client.helper import BMP_service, DS_service, LSM_service, SCD_service
from multiprocessing.spawn import prepare
from bluepy.btle import *
import sys
from helper import *
import time
import datetime
from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import http.client, urllib
import logging as log

token = "m1gTOsTToWUNZP-CWvZa0vIS5T2o-4_48dvQ8sgw4N-Lk2i5aQnOIBy2ycYwQB57x9Inu-1KQwj17IGUzKL-AA=="
org = "ciber"
bucket = "final_test"
Address = 'cf:d8:b3:75:d1:d5'

# Initializing logging info for the log file.
format = "%(asctime)s.%(msecs)03d: %(message)s"
log.basicConfig(filename="logfile.log",
                    filemode="a",
                    format=format,
                    level = log.INFO,
                    datefmt="%H:%M:%S")


def send_message(_msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a8q76apfdh5smhxg6k234yc1djzr8r",
        "user": "a32wsusbc7ouc64jfuhm8dgqi778js",
        "message": _msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def onboard_sensor_process():
    counter=0
    while True:
        try:
            per = connect_device(Onbard_sensor_Address)
            print_svcs(per)
           
            print("Enabling All On-board Sensors...\n")
            SHT = SHT_service(periph=per)
            APDS = APDS_service(periph=per)
            BMP = BMP_service(periph=per)
            LSM = LSM_service(periph=per)
            SCD = SCD_service(periph=per)
            DS = DS_service(periph=per, UUID='8121b46f-56ce-487f-9084-5330700681d5')
            
                
            print("Configuring ALL SENSORS...\n")
            SHT.configure()
            APDS.configure()
            BMP.configure()
            LSM.configure()
            SCD.configure()
            DS.configure()
            
             while True:
                if per.waitForNotifications(1.0):
                    continue
           
        except Exception as e:
            per.disconnect()
            log.error("Exception Occured: {}".format(e))
            send_message("Exception Occured: {}".format(e))
            if counter == 15:
                return
            counter+=1
            time.sleep(10)


def DS_sensor_process(address):
    counter=0
    while True:
        try:
            per = connect_device(address)
            print_svcs(per)

            print("Enabling All DS sensors...")
            DS = DS_service(periph=per, UUID='')

            print("Configuring All Sensors...")_
            DS.configure()

            while True:
                if per.waitForNotifications(1.0):
                    continue

        except Exception as e:
            per.disconnect()
            log.error("Exception with DS sensor process Occured: {}".format(e))
            send_message("Exception with DS sensor process Occured: {}".format(e))
            if counter == 15:
                quit()
            counter+=1
            time.sleep(10)
