from bluepy.btle import *

Address = 'cf:d8:b3:75:d1:d5'

per = Peripheral(Address, ADDR_TYPE_RANDOM, iface=0)

print("Connecting to the device\n")

svc = per.getServices()

for s in svc:
    print("Service: ", s)
    
chrc = per.getCharacteristics(25,31)

chrc[0].read()
