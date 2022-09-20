from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

token = "m1gTOsTToWUNZP-CWvZa0vIS5T2o-4_48dvQ8sgw4N-Lk2i5aQnOIBy2ycYwQB57x9Inu-1KQwj17IGUzKL-AA=="
org = "ciber"
bucket = "example_bucket"
url = "http://149.165.159.180:8086"

def write_influx_data(json_body):  
    with InfluxDBClient(url=url, token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)     
        write_api.write(bucket, org, json_body)
        client.close()

def helper_thread_fn(varclass):
    client = InfluxDBClient(url=url, token=token, org=org)
    file = varclass.send_stale_data_influxdb(client,bucket,org)
    print(f"Sent all the data of {file} to influxdb")