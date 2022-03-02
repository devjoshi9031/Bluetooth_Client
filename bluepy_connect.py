from bluepy.btle import *
import sys
from helper import *
Address = 'cf:d8:b3:75:d1:d5'

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
BMP_HUM_UUID = '0x2A6F'

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



def print_svcs(per):
        svc = per.getServices();
        for s in svc:
                ch = s.getCharacteristics()
                for c in ch:
                        print(s.uuid, c)



class notifDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
#         tup = struct.unpack('h', data)
        # ~ dat = binascii.b2a_hex(data)
        dat=int.from_bytes(data, byteorder=sys.byteorder)
        print("Handle: " +str(cHandle)+"Value of the Temp: %.2f",(dat/100))

       
print("Connecting to the device: \n"+str(Address))

# Connect to the peripheral with the address mentioned above.
per = Peripheral(Address, ADDR_TYPE_RANDOM, iface=0)
per.setDelegate(notifDelegate())

print("Successfully connected to the device")


print_svcs(per)

print("Enabling SHT and APDS...\n")
sht = SHT_service(periph=per)
APDS = APDS_service(periph=per)

print("Configuring SHT and APDS...\n")
sht.configure()
APDS.configure()
#APDS.getHandle()

print("Printing the Handles\n")
print_handle()

while True:
    if per.waitForNotifications(1.0):
        continue
        
