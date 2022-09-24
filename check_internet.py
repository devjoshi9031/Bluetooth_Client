from time import time
import urllib.request
import sys
def check_internet(host='http://149.165.159.180:8086'):
    try:
        urllib.request.urlopen(host,timeout=0.2) #Python 3.x
        return True
    except:
        return False
try:
    host = 'http://'+str(sys.argv[1])
except:
    host='http://149.165.159.180:8086'

print(check_internet(host))
