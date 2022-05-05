import multiprocessing as mp
import this
from bluepy.btle import *
import time as t
from helper import *
import http.client, urllib
import logging as log

def print_svcs(per):
    '''
    This will print all the characteristics of all the services in a peripheral connection.
    Useful to know what all characteristics are enabled on the server side.
    '''
    print("Printing Services for address {} ...".format(per.addr))
    services = per.getServices()
    for service in services:
            characteristics = service.getCharacteristics()
            for characteristic in characteristics:
                    print(service.uuid, characteristic)


def connect_device(address):
    '''
    This function will connect to the device with given address BLE device using bluepy module.
    @return: Peripheral object that was returned after connection.
    '''
    print("Connecting to {} device...".format(address))
    per = Peripheral(address, ADDR_TYPE_RANDOM, iface=0)
    if (per.addr == mac_address['DS_Sensor_Board'] or per.addr == mac_address['Dummy']):
        per.setDelegate(notifDelegate_DS_Sensor_Board())
    elif(per.addr == mac_address['All_Sensor_Board']):
        per.setDelegate(notifDelegate_All_Sensor_Board())
    else:
        print("Check Connect_device function. Need proper Delegate class to proper address")
    print("Successfully Connected to {} device\n".format(address))
    return per


def send_message(_msg):
    ''' 
    This function will send an message to the Pushover API, if some exception is raised 
    in the while(True) loop. Just an additional feature.
    '''

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a32wsusbc7ouc64jfuhm8dgqi778js",
        "user": "uq19utktqpezbycu36ijf61pmdzzin",
        "message": _msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

'''
def check_temperature():
    this function should check 
'''
class notifDelegate_All_Sensor_Board(DefaultDelegate):
    '''
    Delegate function. This function will be called everytime a notification is received 
    on the connected peripheral device. This will be set at the time of connection, so single
    class for a single connection. Also the class `handleNotification` will change according
    to the connection type.
    '''
    def __init__(self):
        DefaultDelegate.__init__(self)
			
    def handleNotification(self, cHandle, data):
        dat=int.from_bytes(data, byteorder=sys.byteorder)
        if(cHandle == BATT.battery_chrc.valHandle):
            BATT.battery_data = dat/100
            print("All_Sensors Battery: {:.3f}".format(dat))
            BATT.prepare_influx_data("All_Sensors")
        elif(cHandle==SHT.sht_temp_chrc.valHandle):
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
            if(SCD.scd_hum_is_fresh==True and SCD.scd_temp_is_fresh==True):
                SCD.prepare_influx_data("All_Sensors")

        elif(cHandle == SCD.scd_temp_chrc.valHandle):
            SCD.scd_temp_is_fresh = True
            SCD.scd_temp_data = dat/100
            print("SCD temp value: {}".format(dat/100))
            if(SCD.scd_co2_is_fresh == True and SCD.scd_hum_is_fresh==True):
                SCD.prepare_influx_data("All_Sensors")

        elif(cHandle == SCD.scd_hum_chrc.valHandle):
            SCD.scd_hum_is_fresh=True
            SCD.scd_hum_data = dat/100
            print("SCD humidity value: {}".format(dat))
            if(SCD.scd_temp_is_fresh == True and SCD.scd_co2_is_fresh==True):
                SCD.prepare_influx_data("All_Sensors")

        elif(cHandle == DS.ds_temp_chrcs[0].valHandle):
            DS.ds_temp_is_fresh[0]=True
            DS.ds_temp_datas[0] = (dat/100)
            print("DS temp1: {}".format(dat/100))
            DS.prepare_influx_data("All_Sensors")

        elif(cHandle == BME.bme_tvoc_chrc.valHandle):
            BME.bme_tvoc_data=dat
            print("ALl Sensors BME_TVOC: {}".format(dat))
            BME.prepare_influx_data("All_Sensors")




class notifDelegate_DS_Sensor_Board(DefaultDelegate):
    '''
    Delegate function. This function will be called everytime a notification is received 
    on the connected peripheral device. This will be set at the time of connection, so single
    class for a single connection. Also the class `handleNotification` will change according
    to the connection type.
    '''
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        dat=int.from_bytes(data, byteorder=sys.byteorder)
        if(cHandle == DS_SENSOR_DS.ds_temp_chrcs[0].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[0]=True
            DS_SENSOR_DS.ds_temp_datas[0] = ((dat>>8)/100)
            print("Address: {}\tDS temp1: {}".format(hex(dat&0xFF),DS_SENSOR_DS.ds_temp_datas[0]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[1].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[1]=True
            DS_SENSOR_DS.ds_temp_datas[1] = ((dat>>8)/100)
            print("Address: {}\tDS temp2: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[1]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[2].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[2]=True
            DS_SENSOR_DS.ds_temp_datas[2] = ((dat>>8)/100)
            print("Address: {}\tDS temp3: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[2]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[3].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[3]=True
            DS_SENSOR_DS.ds_temp_datas[3] = ((dat>>8)/100)
            print("Address: {}\tDS temp4: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[3]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")


        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[4].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[4]=True
            DS_SENSOR_DS.ds_temp_datas[4] = ((dat>>8)/100)
            print("Address: {}\tDS temp5: {}".format(hex(dat&0xFF),DS_SENSOR_DS.ds_temp_datas[4]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[5].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[5]=True
            DS_SENSOR_DS.ds_temp_datas[5] = ((dat>>8)/100)
            print("Address: {}\tDS temp6: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[5]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[6].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[6]=True
            DS_SENSOR_DS.ds_temp_datas[6] = ((dat>>8)/100)
            print("Address: {}\tDS temp7: {}".format(hex(dat&0xFF),DS_SENSOR_DS.ds_temp_datas[6]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[7].valHandle):
            DS_SENSOR_DS.ds_temp_is_fresh[7]=True
            DS_SENSOR_DS.ds_temp_datas[7] = ((dat>>8)/100)
            print("Address: {}\tDS temp8: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[7]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_BATT.battery_chrc.valHandle):
            DS_SENSOR_BATT.battery_data = dat/100
            print("Only DS Sensor Battery: {:.3f}".format(DS_SENSOR_BATT.battery_data))
            DS_SENSOR_BATT.prepare_influx_data("Only_DS_Sensors")


def thread1():
    ''' 
    THREAD1 FUNCTION:

    This function will be used by the first thread. It will connect to the all_sensor_board.
    Continously wait for the notification.
    '''
    while(True):
        try:
            peripheral=None
            print("Thread 1: Connecting to peripheral!!!")

            # notifdelegate class needs to access these classes, so make them global.
            global SHT, APDS, BMP, LSM, SCD, DS, BATT, BME

            peripheral = connect_device(mac_address[str(mp.current_process().name)])
            print_svcs(peripheral)
            print("Thread 1: Initiating all the sensor classes!!!")
            SHT = SHT_service(periph=peripheral)
            APDS = APDS_service(periph=peripheral)
            BMP = BMP_service(periph=peripheral)
            LSM = LSM_service(periph=peripheral)
            SCD = SCD_service(periph=peripheral)
            DS = DS_service(periph=peripheral, UUID='8121b46f-56ce-487f-9084-5330700681d5', num_sensors=1)
            BATT = Battery_service(periph=peripheral, UUID='c9e3205e-f994-4ff0-8300-9b703aecae08', BATTERY_VAL_UUID='3d84bece-189c-4bc7-9f10-512173ed8eaa')
            BME = BME_service(periph=peripheral, UUID='54adba22-25c7-49d2-b4be-dbbb1a77efa3')

            print("Thread 1: Configuring all the sensor classes!!!")
            BATT.configure()
            SHT.configure()
            APDS.configure()
            BMP.configure()
            LSM.configure()
            SCD.configure()
            DS.configure()
            BME.configure()

            print("Thread 1: Done Configuration! Waiting for notification!!")
            
            
            # Wait indefinitely to receive notifications from the connection
            while True:
                if peripheral.waitForNotifications(1.0):
                    continue
        # Try and except will make sure the code doesn't stop.
        # Disconnect and notify user about the exception.
        except Exception as e:
            if(peripheral is not None):
                peripheral.disconnect()
            print("Thread 1: Exception: {}".format(e))
            # send_message("Thread 1: Exception: {}".format(e))
            time.sleep(10)


def thread2():
    while(True):
        try:
            peripheral=None
            t.sleep(10)
            print("Thread 2: Connecting to peripheral!!!")
            peripheral = connect_device(mac_address[str(mp.current_process().name)])
            print_svcs(peripheral)
            # notifdelegate class needs to access this class, so make it global
            global DS_SENSOR_DS, DS_SENSOR_BATT
            print("Thread 2: Initiating DS sensor class!!!")
            DS_SENSOR_DS = DS_service(periph=peripheral, UUID='e66e54fc-4231-41ae-9663-b43f50cfcb3b', num_sensors=8)
            DS_SENSOR_BATT = Battery_service(periph=peripheral, UUID='b9ad8153-8145-4575-9d1a-ab745b5b2d08', BATTERY_VAL_UUID='e0482d82-3a6f-4f52-b35f-c86eda8747fd')
            print("Thread 2: Configuring DS sensor class!!!")
            DS_SENSOR_DS.configure()
            DS_SENSOR_BATT.configure()

            print("Thread 2: Done Configuration! Waiting for notification!!")
            # Wait indefinitely to receive notifications from the connection.
            while True:
                if peripheral.waitForNotifications(1.0):
                    continue
        
        # Try and except will make sure the code doesn't stop.
        # Disconnect and notify user about the exception.
        except Exception as e:
            if(peripheral is not None):
                peripheral.disconnect()
            print("Thread 2: Exception: {}".format(e))
            send_message("Thread 2: Exception: {}".format(e))
            time.sleep(10)

# Mac address list to store the address of the sensor boards.
mac_address={'Dummy':'DE:F7:1D:89:55:D5', 'All_Sensor_Board': 'CF:D8:B3:75:D1:D5','DS_Sensor_Board': 'FC:9A:71:3C:E4:B8'}
# List to store the number of processes.
proc_list=[]

# Code to run for the main process.
if __name__ == "__main__":
    # Make two processes and append them in the list.
    proc_list.append(mp.Process(target=thread1, name="All_Sensor_Board"))
    proc_list.append(mp.Process(target=thread2, name="DS_Sensor_Board"))

# TODO: Need to support signalling between threads to make sure if a process is stuck we
        # should be able to restart a thread.
    proc_list[0].start()
    proc_list[1].start()
    proc_list[0].join()
    proc_list[1].join()





