import time
import sys
import csv
import os
from turtle import write_docstringdict
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

def init_influxdb_personal():
    token = "bur0bJ1SxU0-vAW9h7vMocbjJspf5cOtlcPjrsjlFbMt3FUsRJY2GfZRLz3Sy--QkMuWQbmfeIAcotAXMYciQw=="
    org = "joshidev22214@gmail.com"
    url = "https://us-west-2-2.aws.cloud2.influxdata.com"
    return token,org,url

def init_influxdb_university():
    token = "m1gTOsTToWUNZP-CWvZa0vIS5T2o-4_48dvQ8sgw4N-Lk2i5aQnOIBy2ycYwQB57x9Inu-1KQwj17IGUzKL-AA=="
    org = "ciber"
    url = "http://149.165.159.180:8086"
    return token,org,url
    
def send_APDS_Data(client_api,bucket,org):
    file = open(sys.argv[1])
    csvfilereader = csv.reader(file)
    header = next(csvfilereader)
    print("Header: {}".format(header))
    write_api = client_api.write_api(write_options=SYNCHRONOUS)
    while(1):
        try:
            for row in csvfilereader:
                point = (
                        Point("APDS")
                        .time(row[0])
                        .tag("Board", row[1])
                        # .tag("Measurement","APDS")
                        .field("Clear_Light", float(row[2]))
                        
                        # .time(datetime.utcnow(), )
                    )
                write_api.write(bucket=bucket,org=org,record=point)
                print(point)
        
        except Exception as e:
            print(e)

        else:
            # os.remove(sys.argv[1])
            # with open(sys.argv[1], "w") as csv_fp:
            #     writer = csv.writer(csv_fp)
            #     writer.writerow(header)
            break
    file.close()
    return

def send_dummy_data(client_api,bucket,org):
    write_api = client_api.write_api(write_options=SYNCHRONOUS)
    for value in range(5):
        point = (
            Point("Dummy")
            .tag("Board","Dummy board")
            .field("Dummy_value", (value))
            # .time(str(time.ctime()))
        )
        print(point)
        print(write_api.write(bucket=bucket,org=org,record=point))
    
def main():
    token,org,url = init_influxdb_university()
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    bucket = "example_bucket"
    send_APDS_Data(client,bucket,org)
    # send_dummy_data(client,bucket,org)
         


if __name__ == "__main__":
    main()