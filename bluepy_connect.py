#!/usr/bin/env python
# from Bluetooth_Client.helper import BMP_service, DS_service, LSM_service, SCD_service
from multiprocessing.spawn import prepare
from attr import field
from bluepy.btle import *
import sys
from helper import *
import time
import sys
import datetime
from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import http.client, urllib

# This is the information required for the influx_db setup. Change the name of the bucket if .
token = "m1gTOsTToWUNZP-CWvZa0vIS5T2o-4_48dvQ8sgw4N-Lk2i5aQnOIBy2ycYwQB57x9Inu-1KQwj17IGUzKL-AA=="
org = "ciber"
bucket = "final_test_10_mins_delay"


Address = 'FC:9A:71:3C:E4:B8'

'''
SHT_PRI_UUID = '57812a99-9146-4e72-a4b7-5159632dee90'
SHT_TEMP_UUID = '0x2A6E'
SHT_HUM_UUID = '0x2A6F'
APDS_PRI_UUID = 'ebcc60b7-974c-43e1-a973-426e79f9bc6c'
APDS_PROX_UUID = '1441e94a-74bc-4412-b45b-f1d91487afe5'
APDS_RED_UUID = '3c321537-4b8e-4662-93f9-cb7df0e437c5'
APDS_BLUE_UUID = '3c321537-4b8e-4662-93f9-cb7df0e437c5'
APDS_GREEN_UUID = '3c321537-4b8e-4662-93f9-cb7df0e437c5'
APDS_CLEAR_UUID = '3c321537-4b8e-4662-93f9-cb7df0e437c5'

BMP_PRIM_UUID = 'f4356abe-b85f-47c7-ab4e-54df8f4ad025'
BMP_TEMP_UUID = '0x2A6E'
BMP_HUM_UUID = '0x2A6D'

LSM_PRIM_UUID = 'e82bd800-c62c-43d5-b03f-c7381b38892a'
LSM_ACCELX_UUID = '461d287d-1ccd-46bf-8498-60139deeeb27'
LSM_ACCELY_UUID = 'a32f4917-d566-4273-b435-879eb85bd5cd'
LSM_ACCELZ_UUID = 'e6837dcc-ff0b-4329-a271-c3269c61b10d'
LSM_GYROX_UUID = '54adba22-25c7-49d2-b4be-dbbb1a77efa3'
LSM_GYROY_UUID = '67b2890f-e716-45e8-a8fe-4213db675224'
LSM_GYROZ_UUID = 'af11d0a8-169d-408b-9933-fefd482cdcc6'

SCD_PRIM_UUID = 'fb3047b4-df00-4eb3-9587-3b00e5bb5791'
SCD_CO2_UUID = 'b82febf7-93f8-93f8-8f52-b4797e33aab1'
SCD_TEMP_UUID = '0x2A6E'
SCD_HUM_UUID = '0x2A6F'

DS_UUID = '8121b46f-56ce-487f-9084-5330700681d5'

CCCD_UUID = '2902'

Primary_svcs = [SHT_UUID, APDS_UUID, BMP_UUID, LSM_UUID, SCD_UUID, DS_UUID]
'''

def send_message(_msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a8q76apfdh5smhxg6k234yc1djzr8r",
        "user": "uq19utktqpezbycu36ijf61pmdzzin",
        "message": _msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()




def prepare_influx_data(_measurement):        
    iso = time.ctime()
    if(_measurement == "SHT31"):
        SHT.tempisfresh=False
        SHT.humisfresh=False       
        json_body = [
        {
            "measurement": "SHT31",
                "time_t": iso,
                "fields": {
                    "Temperature": SHT.sht_temp_data,
                    "Humidity": SHT.sht_hum_data,
                }
            }
        ]
    elif(_measurement == "APDS"):
        json_body = [
        {
            "measurement": "APDS",
                "time_t": iso,
                "fields": {
                    "Clear_Light": APDS.apds_clear_data,
                }
            }
        ]
    
    elif(_measurement == "BMP"):
        BMP.tempisfresh = False
        BMP.pressisfresh = False
        json_body = [
        {
            "measurement": "BMP",
                "time_t": iso,
                "fields": {
                    "Temperature": BMP.bmp_temp_data,
                    "Pressure": BMP.bmp_press_data,
                }
            }
        ]
    elif(_measurement == "LSM"):
        LSM.lsm_accelx_is_fresh=False
        LSM.lsm_accely_is_fresh=False
        LSM.lsm_accelz_is_fresh=False
        json_body = [
        {
            "measurement": "LSM",
                "time_t": iso,
                "fields": {
                    "Accel_X": LSM.lsm_accelx_data,
                    "Accel_Y": LSM.lsm_accely_data,
                    "Accel_Z": LSM.lsm_accelz_data,
                }
            }
        ]
    elif(_measurement=="SCD"):
        SCD.scd_co2_is_fresh=False
        SCD.scd_temp_is_fresh=False
        SCD.scd_hum_is_fresh=False
        json_body = [
        {
            "measurement": "SCD",
                "time_t": iso,
                "fields": {
                    "Temperature": SCD.scd_temp_data,
                    "Humidity": SCD.scd_hum_data,
                    "Gas": SCD.scd_co2_data,
                }
            }
        ]
    elif(_measurement=="DS"):
        DS.ds_temp1_is_fresh=False
        DS.ds_temp2_is_fresh=False
        DS.ds_temp3_is_fresh=False
        DS.ds_temp4_is_fresh=False
        DS.ds_temp5_is_fresh=False
        json_body = [
        {
            "measurement": _measurement,
            "time_t":iso,
            "fields": {
                "Temperature1": DS.ds_temp1_data,
                "Temperature2": DS.ds_temp2_data,
                "Temperature3": DS.ds_temp3_data,
                "Temperature4": DS.ds_temp4_data,
                "Temperature5": DS.ds_temp5_data,
            }
            
            }
        ]
    else:
        print("No JSON CREATED...\n")
        return
        
    write_influx_data(json_body)
        
def write_influx_data(json_body):  
    with InfluxDBClient(url="http://149.165.168.73:8086", token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)     
        write_api.write(bucket, org, json_body)
        client.close()


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
        if(cHandle==SHT.sht_temp_chrc.valHandle):
            SHT.tempisfresh = True
            # Make something here to make sure that this is a fresh data
            SHT.sht_temp_data = dat/100
            print("SHT_Temp : "+str(dat/100)+ " degrees")
            # Check if the humidity data is fresh. If fresh sent it.
            if(SHT.humisfresh == True):
                prepare_influx_data("SHT31")
        elif(cHandle==SHT.sht_hum_chrc.valHandle):
            SHT.humisfresh = True
            SHT.sht_hum_data = dat/100
            print("SHT_Humidity :{} %".format(dat/100))
            if(SHT.tempisfresh == True):
                prepare_influx_data("SHT31")
        elif(cHandle==APDS.apds_clear_chrc.valHandle):
            APDS.apds_clear_data = dat
            # Add code to send it to flux
            print("APDS Clear Light: {}".format(dat))    
            prepare_influx_data("APDS")
        
        elif(cHandle==BMP.bmp_temp_chrc.valHandle):
            BMP.tempisfresh=True
            BMP.bmp_temp_data = dat/100
            print("BMP temp: {}".format(dat/100))
            if (BMP.pressisfresh == True):
                prepare_influx_data("BMP")
               
        elif(cHandle==BMP.bmp_press_chrc.valHandle):
            BMP.pressisfresh=True
            BMP.bmp_press_data = dat/100
            print("BMP Pressure: {}".format(dat/100))
            if(BMP.tempisfresh==True):
                prepare_influx_data("BMP")
        
        elif(cHandle == LSM.lsm_accelx_chrc.valHandle):
            LSM.lsm_accelx_is_fresh=True
            LSM.lsm_accelx_data = (dat-32768)/100
            print("LSM AccelX value: {}".format((dat-32768)/100))
            if(LSM.lsm_accely_is_fresh == True and LSM.lsm_accelz_is_fresh==True):
                prepare_influx_data("LSM")
        
        elif(cHandle == LSM.lsm_accely_chrc.valHandle):
            LSM.lsm_accely_is_fresh=True
            LSM.lsm_accely_data = (dat-32768)/100
            print("LSM AccelY value: {}".format((dat-32768)/100))
            if(LSM.lsm_accelx_is_fresh == True and LSM.lsm_accelz_is_fresh==True):
                prepare_influx_data("LSM")
            
        elif(cHandle == LSM.lsm_accelz_chrc.valHandle):
            LSM.lsm_accelz_is_fresh=True
            LSM.lsm_accelz_data = (dat-32768)/100
            print("LSM AccelZ value: {}".format((dat-32768)/100))
            if(LSM.lsm_accelx_is_fresh == True and LSM.lsm_accely_is_fresh==True):
                prepare_influx_data("LSM")
        
        elif(cHandle == SCD.scd_co2_chrc.valHandle):
            SCD.scd_co2_is_fresh=True
            SCD.scd_co2_data = dat
            print("SCD Co2 value: {}".format(dat))
            if(SCD.scd_hum_is_fresh==True and SCD.scd_temp_is_fresh==True):
                prepare_influx_data("SCD")

        elif(cHandle == SCD.scd_temp_chrc.valHandle):
            SCD.scd_temp_is_fresh = True
            SCD.scd_temp_data = dat/100
            print("SCD temp value: {}".format(dat/100))
            if(SCD.scd_co2_is_fresh == True and SCD.scd_hum_is_fresh==True):
                prepare_influx_data("SCD")

        elif(cHandle == SCD.scd_hum_chrc.valHandle):
            SCD.scd_hum_is_fresh=True
            SCD.scd_hum_data = dat/100
            print("SCD temp value: {}".format(dat))
            if(SCD.scd_temp_is_fresh == True and SCD.scd_co2_is_fresh==True):
                prepare_influx_data("SCD")

        elif(cHandle == DS.ds_temp1_chrc.valHandle):
            DS.ds_temp1_is_fresh=True
            DS.ds_temp1_data = (dat/100)
            print("DS temp1: {}".format(dat/100))
            if(DS.ds_temp2_is_fresh == True and 
                DS.ds_temp3_is_fresh == True and 
                DS.ds_temp4_is_fresh == True and 
                DS.ds_temp5_is_fresh == True):
                prepare_influx_data("DS")

        elif(cHandle == DS.ds_temp2_chrc.valHandle):
            DS.ds_temp2_is_fresh=True
            DS.ds_temp2_data = (dat/100)
            print("DS temp2: {}".format(dat/100))
            if(DS.ds_temp1_is_fresh == True and 
                DS.ds_temp3_is_fresh == True and 
                DS.ds_temp4_is_fresh == True and 
                DS.ds_temp5_is_fresh == True):
                prepare_influx_data("DS")

        elif(cHandle == DS.ds_temp3_chrc.valHandle):
            DS.ds_temp3_is_fresh=True
            DS.ds_temp3_data = (dat/100)
            print("DS temp3: {}".format(dat/100))
            if(DS.ds_temp1_is_fresh == True and 
                DS.ds_temp2_is_fresh == True and 
                DS.ds_temp4_is_fresh == True and 
                DS.ds_temp5_is_fresh == True):
                prepare_influx_data("DS")

        elif(cHandle == DS.ds_temp4_chrc.valHandle):
            DS.ds_temp4_is_fresh=True
            DS.ds_temp4_data = (dat/100)
            print("DS temp4: {}".format(dat/100))
            if(DS.ds_temp1_is_fresh == True and 
                DS.ds_temp2_is_fresh == True and 
                DS.ds_temp3_is_fresh == True and 
                DS.ds_temp5_is_fresh == True):
                prepare_influx_data("DS")

        elif(cHandle == DS.ds_temp5_chrc.valHandle):
            DS.ds_temp5_is_fresh
            DS.ds_temp5_data = (dat/100)
            print("DS temp5: {}".format(dat/100))
            if(DS.ds_temp1_is_fresh == True and 
                DS.ds_temp2_is_fresh == True and 
                DS.ds_temp3_is_fresh == True and 
                DS.ds_temp4_is_fresh == True):
                prepare_influx_data("DS")
    

while(1):
    # try:       
    per = connect_device(Address)
    print_svcs(per)

    print("Enabling ALL SENSORS...\n")
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

    print("Done Configuring sensors...\n")
    while True:
        if per.waitForNotifications(1.0):
            continue
    # except Exception as e:
    #     print("Exception: {}".format(e))
    #     send_message("Please check Connection! Exception: {}".format(e))
    #     break