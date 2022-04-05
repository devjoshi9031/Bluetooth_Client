import time
import sys
import datetime
from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
#import RPi.GPIO as GPIO

# You can generate an API token from the "API Tokens Tab" in the UI
token = "m1gTOsTToWUNZP-CWvZa0vIS5T2o-4_48dvQ8sgw4N-Lk2i5aQnOIBy2ycYwQB57x9Inu-1KQwj17IGUzKL-AA=="
org = "ciber"
bucket = "final_test"

session = "dev"
now = datetime.datetime.now()
runNo = now.strftime("%Y%m%d%H%M")
print ("Session: ", session)
print ("runNo: ", runNo)
seed(runNo)
json_body_final = []
def prepare_influx_data(age,something, rep):        
        op = int(random()%10)
        print("Here is the value of op: " +str(op))

        iso = time.ctime()
        
        json_body = [
        {
            "measurement": session,
                # "tags": {
                #     "run": runNo,
                #     },
                "time_t": iso,
                "fields": {
                    # "Name" : name,# "op2" : op1,
                    "Age": age,
                    "Something": something,
                    # "isProgrammer": true,
                    # "hobbies": ["Biking", "Bowling"],
                }
            }
        ]
        json_body_final.append(json_body)
        print("Here is the json bodt:" +str(json_body_final))
        
def write_influx_data(rep):
    for i in range(0,rep):  
        with InfluxDBClient(url="http://149.165.168.73:8086", token=token, org=org) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)     
            write_api.write(bucket, org, json_body_final[i])
            client.close()

a = int(input("HOw many times you want to run the code: "))
for i in range(0,a):
    # name = input("Write the name")
    age = i*100
    # some = float(input("Write something in float data type"))
    prepare_influx_data(age, i, a)
write_influx_data(a)

# client.close()
# # Set this variables, influxDB should be localhost on Pi
# host = "149.165.168.73"
# port = 8086
# user = "ciber"
# password = "Anthophila#17"

# # The database we created
# dbname = "test"
# # Sample period (s)
# interval = 1

# # For GPIO
# # channel = 14¬
# # GPIO.setmode(GPIO.BCM)¬
# # GPIO.setup(channel, GPIO.IN)¬

# # Allow user to set session and runno via args otherwise auto-generate



# # Create the InfluxDB object
# # client = InfluxDBClient(host, port, user, password, dbname)

# # Run until keyboard out
# try:
#     while True:
#         # This gets a dict of the three values
#         op = random()
#         # gpio = GPIO.input(channel)
#         # print (vsense)
#         # print (op)
#         iso = time.ctime()

#         json_body = [
#         {
#           "measurement": session,
#               "tags": {
#                   "run": runNo,
#                   },
#               "time": iso,
#               "fields": {
#                   "op1" : op,
#                 #   "vsense1" : vsense['one'],"vsense2" : vsense['two'],"vsense3" : vsense['three']
#                   # ,"gpio" : gpio
#               }
#           }
#         ]

#         # Write JSON to InfluxDB
#         client.write_points(json_body)
#         # Wait for next sample
#         time.sleep(interval)

# except KeyboardInterrupt:
#     pass