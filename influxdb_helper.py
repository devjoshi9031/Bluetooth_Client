from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


token = "m1gTOsTToWUNZP-CWvZa0vIS5T2o-4_48dvQ8sgw4N-Lk2i5aQnOIBy2ycYwQB57x9Inu-1KQwj17IGUzKL-AA=="
org = "ciber"
bucket = "final_test"


def prepare_influx_data(_measurement):        
    iso = time.ctime()
    if(_measurement == "SHT31"):
        SHT.tempisfresh=False
        SHT.humisfresh=False       
        json_body = [
        {
            "measurement": "SHT31",
                "time_t": iso,
                "fields": {
                    "Temperature": SHT.sht_temp_data,
                    "Humidity": SHT.sht_hum_data,
                }
            }
        ]
    elif(_measurement == "APDS"):
        json_body = [
        {
            "measurement": "APDS",
                "time_t": iso,
                "fields": {
                    "Clear_Light": APDS.apds_clear_data,
                }
            }
        ]
    
    elif(_measurement == "BMP"):
        BMP.tempisfresh = False
        BMP.pressisfresh = False
        json_body = [
        {
            "measurement": "BMP",
                "time_t": iso,
                "fields": {
                    "Temperature": BMP.bmp_temp_data,
                    "Pressure": BMP.bmp_press_data,
                }
            }
        ]
    elif(_measurement == "LSM"):
        LSM.lsm_accelx_is_fresh=False
        LSM.lsm_accely_is_fresh=False
        LSM.lsm_accelz_is_fresh=False
        json_body = [
        {
            "measurement": "LSM",
                "time_t": iso,
                "fields": {
                    "Accel_X": LSM.lsm_accelx_data,
                    "Accel_Y": LSM.lsm_accely_data,
                    "Accel_Z": LSM.lsm_accelz_data,
                }
            }
        ]
    elif(_measurement=="SCD"):
        SCD.scd_co2_is_fresh=False
        SCD.scd_temp_is_fresh=False
        SCD.scd_hum_is_fresh=False
        json_body = [
        {
            "measurement": "SCD",
                "time_t": iso,
                "fields": {
                    "Temperature": SCD.scd_temp_data,
                    "Humidity": SCD.scd_hum_data,
                    "Gas": SCD.scd_co2_data,
                }
            }
        ]
    elif(_measurement=="DS"):
        DS.ds_temp1_is_fresh=False
        DS.ds_temp2_is_fresh=False
        DS.ds_temp3_is_fresh=False
        DS.ds_temp4_is_fresh=False
        DS.ds_temp5_is_fresh=False
        json_body = [
        {
            "measurement": _measurement,
            "time_t":iso,
            "fields": {
                "Temperature1": DS.ds_temp1_data,
                "Temperature2": DS.ds_temp2_data,
                "Temperature3": DS.ds_temp3_data,
                "Temperature4": DS.ds_temp4_data,
                "Temperature5": DS.ds_temp5_data,
            }
            
            }
        ]
    else:
        print("No JSON CREATED...\n")
        return
        
    write_influx_data(json_body)
        
def write_influx_data(json_body):  
    with InfluxDBClient(url="http://149.165.168.73:8086", token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)     
        write_api.write(bucket, org, json_body)
        client.close()
