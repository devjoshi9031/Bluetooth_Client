import multiprocessing as mp
from bluepy.btle import *
import time as t
from helper import *
import traceback
import urllib.request

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
    if (per.addr == mac_address['DS_Sensor_Board'] or per.addr == mac_address['Dummy_DS_Sensor_Board']):
        per.setDelegate(notifDelegate_DS_Sensor_Board())
    elif(per.addr == mac_address['All_Sensor_Board'] or per.addr == mac_address['Dummy_All_Sensor_Board']):
        per.setDelegate(notifDelegate_All_Sensor_Board())
    else:
        print("Check Connect_device function. Need proper Delegate class to proper address")
    print("Successfully Connected to {} device\n".format(address))
    return per

def check_internet(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False


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
        # Things for process signaling.
        # thread1_period_end = t.time()
        # thread1_event.set()
        dat=int.from_bytes(data, byteorder=sys.byteorder)
        if(cHandle == BATT.battery_chrc.valHandle):
            BATT.battery_data = dat/100
            print("All_Sensors Battery: {:.3f}".format(dat))
            if(check_internet()):
                BATT.prepare_influx_data("All_Sensors")
            BATT.append_csv_data("All_Sensors")
        elif(cHandle==SHT.sht_temp_chrc.valHandle):
            SHT.sht_temp_is_fresh = True
            # Make something here to make sure that this is a fresh data
            SHT.sht_temp_data = dat/100
            print("SHT_Temp : "+str(dat/100)+ " degrees")
            # Check if the humidity data is fresh. If fresh sent it.
            if(SHT.sht_hum_is_fresh == True ):
                if(check_internet()):
                    SHT.prepare_influx_data("All_Sensors")
                SHT.append_csv_data("All_Sensors")

        elif(cHandle==SHT.sht_hum_chrc.valHandle):
            SHT.sht_hum_is_fresh = True
            SHT.sht_hum_data = dat/100
            print("SHT_Humidity :{} %".format(dat/100))
            if(SHT.sht_temp_is_fresh == True):
                if(check_internet()):
                    SHT.prepare_influx_data("All_Sensors")
                SHT.append_csv_data("All_Sensors")

        elif(cHandle==APDS.apds_clear_chrc.valHandle):
            APDS.apds_clear_data = dat
            # Add code to send it to flux
            print("APDS Clear Light: {}".format(dat))    
            if(check_internet()):
                APDS.prepare_influx_data("All_Sensors")
            APDS.append_csv_data("All_Sensors")
        
        elif(cHandle==BMP.bmp_temp_chrc.valHandle):
            BMP.bmp_temp_is_fresh=True
            BMP.bmp_temp_data = dat/100
            print("BMP temp: {}".format(dat/100))
            if (BMP.bmp_press_is_fresh == True):
                if(check_internet()):
                    BMP.prepare_influx_data("All_Sensors")
                BMP.append_csv_data("All_Sensors")
            
        elif(cHandle==BMP.bmp_press_chrc.valHandle):
            BMP.bmp_press_is_fresh=True
            BMP.bmp_press_data = dat/10
            print("BMP Pressure: {}".format(dat/10))
            if(BMP.bmp_temp_is_fresh==True):
                if(check_internet()):
                    BMP.prepare_influx_data("All_Sensors")
                BMP.append_csv_data("All_Sensors")
        
        elif(cHandle == LSM.lsm_accelx_chrc.valHandle):
            LSM.lsm_accelx_is_fresh=True
            LSM.lsm_accelx_data = (dat-32768)/100
            print("LSM AccelX value: {}".format((dat-32768)/100))
            if(LSM.lsm_accely_is_fresh == True and LSM.lsm_accelz_is_fresh==True ):
                if(check_internet()):
                    LSM.prepare_influx_data("All_Sensors")
                LSM.append_csv_data("All_Sensors")
        
        elif(cHandle == LSM.lsm_accely_chrc.valHandle):
            LSM.lsm_accely_is_fresh=True
            LSM.lsm_accely_data = (dat-32768)/100
            print("LSM AccelY value: {}".format((dat-32768)/100))
            if(LSM.lsm_accelx_is_fresh == True and LSM.lsm_accelz_is_fresh==True):
                if(check_internet()):
                    LSM.prepare_influx_data("All_Sensors")
                LSM.append_csv_data("All_Sensors")
            
        elif(cHandle == LSM.lsm_accelz_chrc.valHandle):
            LSM.lsm_accelz_is_fresh=True
            LSM.lsm_accelz_data = (dat-32768)/100
            print("LSM AccelZ value: {}".format((dat-32768)/100))
            if(LSM.lsm_accelx_is_fresh == True and LSM.lsm_accely_is_fresh==True):
                if(check_internet()):
                    LSM.prepare_influx_data("All_Sensors")
                LSM.append_csv_data("All_Sensors")
        
        elif(cHandle == SCD.scd_co2_chrc.valHandle):
            SCD.scd_co2_is_fresh=True
            SCD.scd_co2_data = dat
            print("SCD Co2 value: {}".format(dat))
            if(SCD.scd_hum_is_fresh==True and SCD.scd_temp_is_fresh==True):
                if(check_internet()):
                    SCD.prepare_influx_data("All_Sensors")
                SCD.append_csv_data("All_Sensors")


        elif(cHandle == SCD.scd_temp_chrc.valHandle):
            SCD.scd_temp_is_fresh = True
            SCD.scd_temp_data = dat/100
            print("SCD temp value: {}".format(dat/100))
            if(SCD.scd_co2_is_fresh == True and SCD.scd_hum_is_fresh==True):
                if(check_internet()):
                    SCD.prepare_influx_data("All_Sensors")
                SCD.append_csv_data("All_Sensors")


        elif(cHandle == SCD.scd_hum_chrc.valHandle):
            SCD.scd_hum_is_fresh=True
            SCD.scd_hum_data = dat/100
            print("SCD humidity value: {}".format(dat/100))
            if(SCD.scd_temp_is_fresh == True and SCD.scd_co2_is_fresh==True):
                if(check_internet()):
                    SCD.prepare_influx_data("All_Sensors")
                SCD.append_csv_data("All_Sensors")


        elif(cHandle == DS.ds_temp_chrcs[0].valHandle):
            DS.ds_temp_is_fresh[0]=True
            DS.ds_temp_datas[0] = (dat/100)
            print("DS temp1: {}".format(dat/100))
            if(check_internet()):
                DS.prepare_influx_data("All_Sensors")
            DS.append_csv_data("All_Sensors")

        elif(cHandle == BME.bme_tvoc_chrc.valHandle):
            BME.bme_tvoc_data=dat
            print("ALl Sensors BME_TVOC: {}".format(dat))
            if(check_internet()):
                BME.prepare_influx_data("All_Sensors")
            BME.append_csv_data("All_Sensors")





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
        # Things for process signaling.
        # thread2_event.set()
        # thread2_period_end=t.time()
        dat=int.from_bytes(data, byteorder=sys.byteorder)
        if(cHandle == DS_SENSOR_DS.ds_temp_chrcs[0].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            # Here we have to give temp_data a list of address and data value.
            # This is redundant for all the chrc handles but let it be for now.
            DS_SENSOR_DS.ds_temp_datas[0] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp1: {}".format(hex(DS_SENSOR_DS.ds_temp_datas[0][0]),DS_SENSOR_DS.ds_temp_datas[0][1]))
            # print("Address: {}\tDS temp1: {}".format(hex(dat&0xFF),DS_SENSOR_DS.ds_temp_datas[0]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                     DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[1].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[1] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp2: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[1]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[2].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[2] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp3: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[2]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[3].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[3] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp4: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[3]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")


        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[4].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[4] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp5: {}".format(hex(dat&0xFF),DS_SENSOR_DS.ds_temp_datas[4]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[5].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[5] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp6: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[5]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[6].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[6] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp7: {}".format(hex(dat&0xFF),DS_SENSOR_DS.ds_temp_datas[6]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[7].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[7] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp8: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[7]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_DS.ds_temp_chrcs[8].valHandle):
            index = DS_SENSOR_DS.put_data_in_appropriate_place(dat&0xFF, ((dat>>8)/100))
            DS_SENSOR_DS.ds_temp_is_fresh[index]=True
            DS_SENSOR_DS.ds_temp_datas[8] = [(dat&0xFF),((dat>>8)/100)]
            print("Address: {}\tDS temp9: {}".format(hex(dat&0xFF), DS_SENSOR_DS.ds_temp_datas[8]))
            if(all(DS_SENSOR_DS.ds_temp_is_fresh)):
                if(check_internet()):
                    DS_SENSOR_DS.prepare_influx_data("Only_DS_Sensors")
                DS_SENSOR_DS.append_csv_data("Only_DS_Sensors")

        elif(cHandle == DS_SENSOR_BATT.battery_chrc.valHandle):
            DS_SENSOR_BATT.battery_data = dat/100
            print("Only DS Sensor Battery: {:.3f}".format(DS_SENSOR_BATT.battery_data))
            if(check_internet()):
                DS_SENSOR_BATT.prepare_influx_data("Only_DS_Sensors")
            DS_SENSOR_BATT.append_csv_data("Only_DS_Sensors")



def thread1():
    ''' 
    THREAD1 FUNCTION:

    This function will be used by the first thread. It will connect to the all_sensor_board.
    Continously wait for the notification.
    '''
    _is_ble_connected_thread1 = False
    while(True):
        try:
            
            print("Thread 1: Connecting to peripheral!!!")

            # notifdelegate class needs to access these classes, so make them global.
            global SHT, APDS, BMP, LSM, SCD, DS, BATT, BME, thread1_period_end
            if(_is_ble_connected_thread1==False):
                peripheral=None
                SHT=APDS=BMP=LSM=SCD=DS=BATT=BME=None
                peripheral = connect_device(mac_address[str(mp.current_process().name)])
                print_svcs(peripheral)
                print("Thread 1: Initiating all the sensor classes!!!")
                SHT = SHT_service(periph=peripheral)
                APDS = APDS_service(periph=peripheral)
                BMP = BMP_service(periph=peripheral)
                LSM = LSM_service(periph=peripheral)
                SCD = SCD_service(periph=peripheral)
                DS = DS_service(periph=peripheral, 
                                UUID='8121b46f-56ce-487f-9084-5330700681d5',
                                num_sensors=1)
                BATT = Battery_service(periph=peripheral, UUID='c9e3205e-f994-4ff0-8300-9b703aecae08',
                                    BATTERY_VAL_UUID='3d84bece-189c-4bc7-9f10-512173ed8eaa')
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
                _is_ble_connected_thread1=True

            print("Thread 1: Done Configuration! Waiting for notification!!")
            
            
            # Wait indefinitely to receive notifications from the connection
            while True:
                if peripheral.waitForNotifications(1.0):
                    continue
        # Try and except will make sure the code doesn't stop.
        # Disconnect and notify user about the exception.
        except BTLEException as e:
            print(traceback.format_exc())
            if(peripheral is not None):
                peripheral.disconnect()
                _is_ble_connected_thread1=False
            print("Thread 1: Bluetooth Exception: {}".format(e))
            send_message("Thread 1: Bluetooth Exception: {}".format(e))
            time.sleep(10)
        except Exception as e:
            print("Other Exception: \n"+str(traceback.format_exc()))


def thread2():
    _is_ble_connected_thread2=False
    while(True):
        try:
            global DS_SENSOR_DS, DS_SENSOR_BATT
            t.sleep(10)
            print("Thread 2: Connecting to peripheral!!!")
            if(_is_ble_connected_thread2==False):
                peripheral=None
                peripheral = connect_device(mac_address[str(mp.current_process().name)])
                print_svcs(peripheral)
                # notifdelegate class needs to access this class, so make it global
                
                print("Thread 2: Initiating DS sensor class!!!")
                DS_SENSOR_DS = DS_service(periph=peripheral, 
                                        UUID='e66e54fc-4231-41ae-9663-b43f50cfcb3b', 
                                        num_sensors=9)
                DS_SENSOR_BATT = Battery_service(periph=peripheral, 
                                                UUID='b9ad8153-8145-4575-9d1a-ab745b5b2d08', 
                                                BATTERY_VAL_UUID='e0482d82-3a6f-4f52-b35f-c86eda8747fd')
                print("Thread 2: Configuring DS sensor class!!!")
                DS_SENSOR_DS.configure()
                DS_SENSOR_BATT.configure()
                _is_ble_connected_thread2=True

            print("Thread 2: Done Configuration! Waiting for notification!!")
            # Wait indefinitely to receive notifications from the connection.
            while True:
                if peripheral.waitForNotifications(1.0):
                    continue
        
        # Try and except will make sure the code doesn't stop.
        # Disconnect and notify user about the exception.
        except BTLEException as e:
            print(traceback.format_exc())
            if(peripheral is not None):
                peripheral.disconnect()
                _is_ble_connected_thread2=False
            print("Thread 2: Bluetooth Exception: {}".format(e))
            send_message("Thread 2: Bluetooth Exception: {}".format(e))
            time.sleep(10)
        except Exception as e:
            print("Other Exception: \n"+str(traceback.format_exc()))
            

# Mac address list to store the address of the sensor boards.
mac_address={'Dummy_DS_Sensor_Board':'DE:F7:1D:89:55:D5','DS_Sensor_Board': 'F9:FB:6E:E2:90:3F',
                'Dummy_All_Sensor_Board': 'FC:9A:71:3C:E4:B8', 'All_Sensor_Board': 'CF:D8:B3:75:D1:D5'}
# List to store the number of processes.
proc_list=[]

#####################################
# Below things will be used once I implement the signalling thing.

# thread1_period_end=t.time()
# thread2_period_end=t.time()
# thread1_event = mp.Event()
# thread2_event = mp.Event()
#####################################

# Code to run for the main process.
if __name__ == "__main__":
    # Make two processes and append them in the list.
    proc_list.append(mp.Process(target=thread1, name="All_Sensor_Board"))
    proc_list.append(mp.Process(target=thread2, name="DS_Sensor_Board"))

# TODO: Need to support signalling between threads to make sure if a process is stuck we
        # should be able to restart a thread.
    proc_list[0].start()
    proc_list[1].start()

# This loop will conitnuously check if both the threads are active or not. 
# If not just respawn that thread and notify user.
    while True:
        if(proc_list[0].is_alive() is False):
            print("THREAD 1 died")
            send_message("Thread 1 Died for some reason. Starting it again!!!")
            proc_list[0]=mp.Process(target=thread1, name="All_Sensor_Board")
            proc_list[0].start()
        elif(proc_list[1].is_alive() is False):
            send_message("Thread 2 Died for some reason. Starting it again!!!")
            proc_list[1]=mp.Process(target=thread2, name="DS_Sensor_Board")
            proc_list[1].start()
        # Wait for 10 minutes before doing anything
        t.sleep(10*60)


    proc_list[0].join()
    proc_list[1].join()



     

# Need to work on the following to get the message passing working.
    # while True:
    #     try:
    #         print("Main Thread Waiting for thread1 period: {}".format((thread1_period_end+(25*60))- t.time()))
    #         # Wait for thread1_event for 25 mins
    #         if(thread1_event.wait((thread1_period_end+(0.5*60))- t.time()) is False):
    #             thread1_period_end=t.time()
    #             print("Thread 1 did not set the event. Terminating and creating one")
    #             if(proc_list[0].is_alive):
    #                 proc_list[0].terminate()
    #             proc_list[0]=mp.Process(target=thread1, name="All_Sensor_Board")
    #             proc_list[0].start()
    #             print(proc_list[0].is_alive())
                
    #         # Wait for thread2_event for 25 mins
    #         if(thread2_event.wait((thread2_period_end+(0.5*60))- t.time()) is False):
    #             thread2_period_end=t.time()
    #             print("Thread 2 did not set the event. Terminating and creating one")
    #             if(proc_list[1].is_alive):
    #                 proc_list[1].terminate()
    #             proc_list[1]=mp.Process(target=thread2, name="Dummy")
    #             proc_list[1].start()
    #         t.sleep(10)

    #     except Exception as e:
    #         send_message("Main Process Error: "+str(e))
    #         time.sleep(1)






