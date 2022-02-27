from bluepy.btle import *
import struct
import sys

Address = 'cf:d8:b3:75:d1:d5'

'''
SHT_UUID = '57812a99-9146-4e72-a4b7-5159632dee90'
APDS_UUID = 'ebcc60b7-974c-43e1-a973-426e79f9bc6c'
BMP_UUID = 'f4356abe-b85f-47c7-ab4e-54df8f4ad025'
LSM_UUID = 'e82bd800-c62c-43d5-b03f-c7381b38892a'
SCD_UUID = 'fb3047b4-df00-4eb3-9587-3b00e5bb5791'
DS_UUID = '8121b46f-56ce-487f-9084-5330700681d5'

Primary_svcs = [SHT_UUID, APDS_UUID, BMP_UUID, LSM_UUID, SCD_UUID, DS_UUID]


SHT_TEMP_UUID = '2A6E'
SHT_HUM_UUID = '2A6F'

'''



chrc_dict = {'SHT':[], 'APDS':[], 'BMP':[], 'LSM':[], 'SCD':[], 'DS':[]}
print(chrc_dict.items())

handle_sht_temp = 27
handle_sht_hum = 30

class notifDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
#         tup = struct.unpack('h', data)
        print(cHandle, data)
        
        

# Connect to the peripheral with the address mentioned above.
per = Peripheral(Address, ADDR_TYPE_RANDOM, iface=0)
per.setDelegate(notifDelegate())

print("Connecting to the device: \n"+str(Address))

# Get all the primary services available with the connection.
svc = per.getServices()

#Iterate over each primary service and get all the characteristics inside each service.
for s in svc:
    ch = s.getCharacteristics()
    for c in ch:
        print(s.uuid, c, c.valHandle)
        # For future use.
        chrc_dict['SHT'].append(c.valHandle)
        # Write One to all CCCDs of all characterstics to enable notification for all the characterstics.
        per.writeCharacteristic(c.valHandle+1, b"\x01\00")

print("Here is the dict obtained: \n", chrc_dict)

# Go into infinte loop and call the HandleNotification from the Delegate object to read the incoming notification.
while True:
    if per.waitForNotifications(1.0):
        continue
        