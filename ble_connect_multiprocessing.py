import multiprocessing as mp
from bluepy.btle import *
import time as t
from helper import *


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



# class notifDelegate_All_Board(DefaultDelegate):
#     def __init__(self):
#         DefaultDelegate.__init__(self)
        
#     def handleNotification(self, cHandle, data):
#         print(data)


def thread1(index):
    global first_pass
    first_pass = True
    while(1):
        try:
            if first_pass:
                print("Thread 1: Making all board class")
                all_board_sensor_class = All_Board_Sensor(Address=mac_address[index])
                all_board_sensor_class.configure_all_sensors()
                all_board_sensor_class.print_svcs()
                all_board_sensor_class.enable_notifications()

                # peripheral = connect_device(mac_address[index])
                # print_svcs(peripheral)
                # SHT = SHT_service(periph=peripheral)
                # APDS = APDS_service(periph=peripheral)
                # BMP = BMP_service(periph=peripheral)
                # LSM = LSM_service(periph=peripheral)
                # SCD = SCD_service(periph=peripheral)
                # DS = DS_service(periph=peripheral, UUID='8121b46f-56ce-487f-9084-5330700681d5', _num_sensors=1)

                # SHT.configure()
                # APDS.configure()
                # BMP.configure()
                # LSM.configure()
                # SCD.configure()
                # DS.configure()
            else:
                print("Trying to reconnect!!!")
                all_board_sensor_class.per = all_board_sensor_class.connect_peripheral(mac_address[index])
                print("Before enable notifications!!!")
                all_board_sensor_class.enable_notifications(all_board_sensor_class.per)

            while True:
                if all_board_sensor_class.per.waitForNotifications(1.0):
                    continue
        except Exception as e:
            print("Exception: {}".format(e))
            # all_board_sensor_class.disable_notifications()
            first_pass=False
            all_board_sensor_class.disconnect_peripheral()


def thread2(index):
    t.sleep(10)
    peripheral = connect_device(mac_address[index])
    print_svcs(peripheral)
    global DS_SENSOR_DS
    DS_SENSOR_DS = DS_service(periph=peripheral, UUID='e66e54fc-4231-41ae-9663-b43f50cfcb3b', num_sensors=5)
    DS_SENSOR_DS.configure()
    while True:
        if peripheral.waitForNotifications(1.0):
            continue

mac_address=['DE:F7:1D:89:55:D5','cf:d8:b3:75:d1:d5']
proc_list=[]
if __name__ == "__main__":
    proc_list.append(mp.Process(target=thread1, name="All_Sensor_Board", args=(1,)))
    proc_list.append(mp.Process(target=thread2, name="DS_Sensor_Board", args=(0,)))
    proc_list[0].start()
    # proc_list[1].start()
    proc_list[0].join()
    # proc_list[1].join()





