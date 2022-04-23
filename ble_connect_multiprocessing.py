import multiprocessing as mp
from bluepy.btle import *
import time as t
from helper import *
import http.client, urllib
import logging as log

def print_svcs(per):
    print("Printing Services for address {} ...".format(per.addr))
    svc = per.getServices()
    for s in svc:
            ch = s.getCharacteristics()
            for c in ch:
                    print(s.uuid, c)


def connect_device(addr):
    print("Connecting to {} device...".format(addr))
    per = Peripheral(addr, ADDR_TYPE_RANDOM, iface=0)
    if per.addr == mac_address[0]:
        per.setDelegate(notifDelegate_DS_Board())
    else:
        per.setDelegate(notifDelegate_All_Board())
    print("Successfully Connected to {} device\n".format(addr))
    return per

class notifDelegate_All_Board(DefaultDelegate):
		def __init__(self):
			DefaultDelegate.__init__(self)
			
		def handleNotification(self, cHandle, data):
			dat=int.from_bytes(data, byteorder=sys.byteorder)
			if(cHandle==SHT.sht_temp_chrc.valHandle):
				SHT.sht_temp_is_fresh = True
				# Make something here to make sure that this is a fresh data
				SHT.sht_temp_data = dat/100
				print("SHT_Temp : "+str(dat/100)+ " degrees")
				# Check if the humidity data is fresh. If fresh sent it.
				if(SHT.sht_hum_is_fresh == True):
					SHT.prepare_influx_data("All_Sensors")

			elif(cHandle==SHT.sht_hum_chrc.valHandle):
				SHT.sht_hum_is_fresh = True
				SHT.sht_hum_data = dat/100
				print("SHT_Humidity :{} %".format(dat/100))
				if(SHT.sht_temp_is_fresh == True):
					SHT.prepare_influx_data("All_Sensors")

			elif(cHandle==APDS.apds_clear_chrc.valHandle):
				APDS.apds_clear_data = dat
				# Add code to send it to flux
				print("APDS Clear Light: {}".format(dat))    
				APDS.prepare_influx_data("All_Sensors")
			
			elif(cHandle==BMP.bmp_temp_chrc.valHandle):
				BMP.bmp_temp_is_fresh=True
				BMP.bmp_temp_data = dat/100
				print("BMP temp: {}".format(dat/100))
				if (BMP.bmp_press_is_fresh == True):
					BMP.prepare_influx_data("All_Sensors")
				
			elif(cHandle==BMP.bmp_press_chrc.valHandle):
				BMP.bmp_press_is_fresh=True
				BMP.bmp_press_data = dat/100
				print("BMP Pressure: {}".format(dat/100))
				if(BMP.bmp_temp_is_fresh==True):
					BMP.prepare_influx_data("All_Sensors")
			
			elif(cHandle == LSM.lsm_accelx_chrc.valHandle):
				LSM.lsm_accelx_is_fresh=True
				LSM.lsm_accelx_data = (dat-32768)/100
				print("LSM AccelX value: {}".format((dat-32768)/100))
				if(LSM.lsm_accely_is_fresh == True and LSM.lsm_accelz_is_fresh==True):
					LSM.prepare_influx_data("All_Sensors")
			
			elif(cHandle == LSM.lsm_accely_chrc.valHandle):
				LSM.lsm_accely_is_fresh=True
				LSM.lsm_accely_data = (dat-32768)/100
				print("LSM AccelY value: {}".format((dat-32768)/100))
				if(LSM.lsm_accelx_is_fresh == True and LSM.lsm_accelz_is_fresh==True):
					LSM.prepare_influx_data("All_Sensors")
				
			elif(cHandle == LSM.lsm_accelz_chrc.valHandle):
				LSM.lsm_accelz_is_fresh=True
				LSM.lsm_accelz_data = (dat-32768)/100
				print("LSM AccelZ value: {}".format((dat-32768)/100))
				if(LSM.lsm_accelx_is_fresh == True and LSM.lsm_accely_is_fresh==True):
					LSM.prepare_influx_data("All_Sensors")
			
			elif(cHandle == SCD.scd_co2_chrc.valHandle):
				SCD.scd_co2_is_fresh=True
				SCD.scd_co2_data = dat
				print("SCD Co2 value: {}".format(dat))
				if(SCD.scd_sht_hum_is_fresh==True and SCD.scd_temp_is_fresh==True):
					SCD.prepare_influx_data("All_Sensors")

			elif(cHandle == SCD.scd_temp_chrc.valHandle):
				SCD.scd_temp_is_fresh = True
				SCD.scd_temp_data = dat/100
				print("SCD temp value: {}".format(dat/100))
				if(SCD.scd_co2_is_fresh == True and SCD.scd_sht_hum_is_fresh==True):
					SCD.prepare_influx_data("All_Sensors")

			elif(cHandle == SCD.scd_hum_chrc.valHandle):
				SCD.scd_sht_hum_is_fresh=True
				SCD.scd_hum_data = dat/100
				print("SCD temp value: {}".format(dat))
				if(SCD.scd_temp_is_fresh == True and SCD.scd_co2_is_fresh==True):
					SCD.prepare_influx_data("All_Sensors")

			elif(cHandle == DS.ds_temp_chrcs[0].valHandle):
				DS.ds_temp_is_fresh[0]=True
				DS.ds_temp_datas[0] = (dat/100)
				print("DS temp1: {}".format(dat/100))
				DS.prepare_influx_data("All_Sensors")

class notifDelegate_DS_Board(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        dat=int.from_bytes(data, byteorder=sys.byteorder)
        if(cHandle == DS_SENSOR_DS.ds_temp_chrcs[0].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[0]=True
            DS_SENSOR_DS.ds_temp_datas[0] = (dat/100)
            print("DS temp1: {}".format(dat/100))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[1].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[1]=True
            DS_SENSOR_DS.ds_temp_datas[1] = (dat/100)
            print("DS temp2: {}".format(dat/100))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[2].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[2]=True
            DS_SENSOR_DS.ds_temp_datas[2] = (dat/100)
            print("DS temp3: {}".format(dat/100))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[3].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[3]=True
            DS_SENSOR_DS.ds_temp_datas[3] = (dat/100)
            print("DS temp4: {}".format(dat/100))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[4].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[4]=True
            DS_SENSOR_DS.ds_temp_datas[4] = (dat/100)
            print("DS temp5: {}".format(dat/100))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")

def send_message(_msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a8q76apfdh5smhxg6k234yc1djzr8r",
        "user": "a32wsusbc7ouc64jfuhm8dgqi778js",
        "message": _msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def thread1(index):
    while(True):
        try:
            print("Thread 1: Making all board class")
            global SHT, APDS, BMP, LSM, SCD, DS
            # all_board_sensor_class = All_Board_Sensor(Address=mac_address[index])
            # all_board_sensor_class.configure_all_sensors()
            # all_board_sensor_class.print_svcs()
            # all_board_sensor_class.enable_notifications()

            peripheral = connect_device(mac_address[index])
            print_svcs(peripheral)
            SHT = SHT_service(periph=peripheral)
            APDS = APDS_service(periph=peripheral)
            BMP = BMP_service(periph=peripheral)
            LSM = LSM_service(periph=peripheral)
            SCD = SCD_service(periph=peripheral)
            DS = DS_service(periph=peripheral, UUID='8121b46f-56ce-487f-9084-5330700681d5', num_sensors=1)

            SHT.configure()
            APDS.configure()
            BMP.configure()
            LSM.configure()
            SCD.configure()
            DS.configure()
            # print("Trying to reconnect!!!")
            # all_board_sensor_class.per = all_board_sensor_class.connect_peripheral(mac_address[index])
            # print("Before enable notifications!!!")
            # all_board_sensor_class.enable_notifications(all_board_sensor_class.per)

            while True:
                if peripheral.waitForNotifications(1.0):
                    continue
        except Exception as e:
            peripheral.disconnect()
            print("Exception: {}".format(e))
            send_message("Exception: {}".format(e))

            time.sleep(10)


def thread2(index):
    while(True):
        try:
            t.sleep(10)
            peripheral = connect_device(mac_address[index])
            print_svcs(peripheral)
            global DS_SENSOR_DS
            DS_SENSOR_DS = DS_service(periph=peripheral, UUID='e66e54fc-4231-41ae-9663-b43f50cfcb3b', num_sensors=5)
            DS_SENSOR_DS.configure()
            while True:
                if peripheral.waitForNotifications(1.0):
                    continue
        except Exception as e:
            peripheral.disconnect()
            print("Exception: {}".format(e))
            send_message("Exception: {}".format(e))
            time.sleep(10)

mac_address=['DE:F7:1D:89:55:D5','cf:d8:b3:75:d1:d5']
proc_list=[]
if __name__ == "__main__":
    proc_list.append(mp.Process(target=thread1, name="All_Sensor_Board", args=(1,)))
    proc_list.append(mp.Process(target=thread2, name="DS_Sensor_Board", args=(0,)))
    proc_list[0].start()
    proc_list[1].start()
    proc_list[0].join()
    proc_list[1].join()





