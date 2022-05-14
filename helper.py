from influxdb_helper import *
import time
from bluepy.btle import *
import http.client, urllib
import csv, os

def send_message(_msg):
    ''' 
    This function will send an message to the Pushover API, if some exception is raised 
    in the while(True) loop. Just an additional feature.
    '''

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a32wsusbc7ouc64jfuhm8dgqi778js",
        "user": "uq19utktqpezbycu36ijf61pmdzzin",
        "message": _msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

class SHT_service():      
	'''
	Class for SHT31 Sensor on Adafruit Feather sense

	This class will be used for the SHT31 sensor on the adafruit feather sense board.
	It will match the UUID given in the primary service list and also get all the charac
	in that service. 

	Members:
		SHT_PRI_UUID -> UUID for the primary service.\n
		self.per -> copy of the peripheral class that we get from BTLE(This will be given while instantiating this class.)\n
		self.sht_temp_chrc ->temperature characteristic.\n
		self.sht_temp_chrc_cccd -> Client Characterstic Configuration Descriptor for temp. chrc.\n
		self.sht_hum_chrc -> Humidity Characteristic \n
		self.sht_hum_chrc_ccd -> Client Characterstic Configuration Descriptor for hum. chrc.\n
		self.sht_temp_data -> Temperature characteristic data. \n
		self.sht_temp_is_fresh -> Current temp. chrc. value is fresh or not?\n
		self.sht_hum_data -> Humidity characteristic data.\n
		self.sht_hum_is_fresh -> Current hum. chrc. value is fresh or not?\n

	Methods:
		getService -> Get the primary service from the given peripheral. \n
		getCharacteristics -> Get the temp & hum. characteristics from the primary service.\n
		getCCCD -> Get the Client Characteristic Configuration Descriptors. \n
		enable_notification -> enable notifications for all chrcs.\n
		disable_notification -> disable notification for all chrcs.\n
		prepare_influx_data -> Once we have fresh data for all chrcs. prepare the data 
								in appropriate json format and send it to influxDB.\n
		configure -> Call all the above methods in proper sequence.\n
	'''

	SHT_TEMP_UUID = '2A6E'
	SHT_HUM_UUID = '2A6F'  
	CCCD_UUID = '2902'
	
	# UUID is optional but given this field just in case we need to use this for another board.
	def __init__(self, periph, UUID='57812a99-9146-4e72-a4b7-5159632dee90'):
		self.SHT_PRI_UUID=UUID
		self.per = periph
		self.sht_svc = None
		self.sht_temp_chrc = None
		self.sht_temp_chrc_cccd = 0
		self.sht_hum_chrc = None
		self.sht_hum_chrc_cccd = 0
		self.sht_temp_is_fresh = False
		self.sht_hum_is_fresh = False
		self.sht_temp_data=0
		self.sht_hum_data=0
		self.csv_file_name = "/home/dev/new/SHT/Local_SHT_Data.csv"
		
	def getService(self):
		self.sht_svc = self.per.getServiceByUUID(self.SHT_PRI_UUID)
	
	def getCharacteristics(self):
		self.sht_temp_chrc = self.sht_svc.getCharacteristics(forUUID=self.SHT_TEMP_UUID)[0]
		self.sht_hum_chrc = self.sht_svc.getCharacteristics(forUUID=self.SHT_HUM_UUID)[0]
			
	def getCCCD(self):
		self.sht_temp_chrc_cccd = self.sht_temp_chrc.getDescriptors(self.CCCD_UUID)[0]
		self.sht_hum_chrc_cccd = self.sht_hum_chrc.getDescriptors(self.CCCD_UUID)[0]
		
	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
	
	def enable_notification(self):
		self.sht_temp_chrc_cccd.write(b"\x01\x00",True)
		self.sht_hum_chrc_cccd.write(b"\x01\x00",True)
	
			
	def disable_notification(self):
		self.sht_temp_chrc_cccd.write(b"\x00\x00",False)
		self.sht_hum_chrc_cccd.write(b"\x00\x00",False)    
			
	def check_data(self):
		'''
		Sends message if the temperature value is non-zero and not in the range [30,39]C.
		Also sends message if the humidity value is non-zero and not in the range [40-60]%.
		'''
		if(self.sht_temp_data !=0 and (self.sht_temp_data <=30.00 or self.sht_temp_data>=39.00)):
			send_message("Critical Temperature Notified in SHT31: {}".format(self.sht_temp_data))
		if(self.sht_hum_data!=0 and (self.sht_hum_data<=40.00 or self.sht_hum_data>=70.00)):
			send_message("Critical Humidity Notified in SHT31: {}".format(self.sht_hum_data))

	def open_csv_file(self):
		header = ["time", "Board", "Temperature", "Humidity"]
		if(os.path.exists(self.csv_file_name)):
			pass			
		
		else:
			with open(self.csv_file_name, "w") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(header)

	def append_csv_data(self,tag):
		time_t = time.ctime()
		data = [time_t, tag, self.sht_temp_data, self.sht_hum_data]
		with open(self.csv_file_name, "a") as self.csv_fp:
			writer = csv.writer(self.csv_fp)
			writer.writerow(data)

	def prepare_influx_data(self, tag):
		self.check_data()
		iso = time.ctime()
		self.sht_sht_hum_is_fresh=False
		self.sht_temp_is_fresh=False
		json_body = [
		{
			"measurement": "SHT",
			"time_t":iso,
			"tags":{
				"Board": tag,
				},
			"fields": {
				"Temperature": self.sht_temp_data,
				"Humidity": self.sht_hum_data,
				}
			}
		]
		write_influx_data(json_body)


	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


class APDS_service():
	'''
	Class for APDS9960 Sensor on Adafruit Feather sense

	This class will be used for the APDS9960 sensor on the adafruit feather sense board.
	It will match the UUID given in the primary service list and also get all the charac
	in that service. 

	Members:
		self.APDS_PRI_UUID -> UUID for the primary service.\n
		self.per -> copy of the peripheral class that we get from BTLE(This will be given while instantiating this class.)\n
		self.apds_clear_chrc ->Clear light characteristic.\n
		self.apds_clear_chrc_cccd -> Client Characterstic Configuration Descriptor for clear_light. chrc.\n
		self.apds_clear_data -> Clear Light characteristic data. \n

	Methods:
		getService -> Get the primary service from the given peripheral. \n
		getCharacteristics -> Get the temp & hum. characteristics from the primary service.\n
		getCCCD -> Get the Client Characteristic Configuration Descriptors. \n
		enable_notification -> enable notifications for all chrcs.\n
		disable_notification -> disable notification for all chrcs.\n
		prepare_influx_data -> Once we have fresh data for all chrcs. prepare the data 
								in appropriate json format and send it to influxDB.\n
		configure -> Call all the above methods in proper sequence.\n
	'''

	CCCD_UUID = '2902'
	
	def __init__(self, periph, UUID='ebcc60b7-974c-43e1-a973-426e79f9bc6c', clearUUID='e960c9b7-e0ed-441e-b22c-d93252fa0fc6'):
		self.APDS_PRI_UUID=UUID
		self.APDS_CLEAR_UUID=clearUUID
		self.per = periph
		self.apds_svc = None
		self.apds_clear_chrc = None
		self.apds_clear_chrc_cccd = 0
		self.apds_clear_data=0
		self.csv_file_name = "/home/dev/new/APDS/Local_APDS_Data.csv"
			
	def getService(self):
		self.apds_svc = self.per.getServiceByUUID(self.APDS_PRI_UUID)
        
	def getCharacteristics(self):
		self.apds_clear_chrc = self.apds_svc.getCharacteristics(forUUID=self.APDS_CLEAR_UUID)[0]
                
	def getCCCD(self):
		self.apds_clear_chrc_cccd = self.apds_clear_chrc.getDescriptors(self.CCCD_UUID)[0]
			
	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
        
	def enable_notification(self):
		self.apds_clear_chrc_cccd.write(b"\x01\x00",True)
                
	def disable_notification(self):  
		self.apds_clear_chrc_cccd.write(b"\x01\x00",False)
	
	def check_data(self):
		'''
		sends message if the APDS clear data is more than 5.
		'''
		if(self.apds_clear_data>=5):
			send_message("***Caution BeeHive Open*** APDS: {}".format(self.apds_clear_data))

	def open_csv_file(self):
		header = ["Time", "Board", "Clear_Light"]
		if(os.path.exists(self.csv_file_name)):
			pass
		else:
			with open(self.csv_file_name, "w+") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(header)

	def append_csv_data(self,tag):
		time_t = time.ctime()
		data = [time_t, tag, self.apds_clear_data]
		with open(self.csv_file_name, "a") as self.csv_fp:
			writer = csv.writer(self.csv_fp)
			writer.writerow(data)

	def prepare_influx_data(self, tag):
		self.check_data()
		iso = time.ctime()
		json_body = [
		{
			"measurement": "APDS",
			"time_t":iso,
			"tags":{
				"Board": tag,
				},
			"fields": {
				"Clear_Light": self.apds_clear_data,
				}
			}
		]
		write_influx_data(json_body)	

	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


	
class LSM_service():
	'''
	Class for LSM6DS33 Sensor on Adafruit Feather sense

	This class will be used for the LSM6DS33 sensor on the adafruit feather sense board.
	It will match the UUID given in the primary service list and also get all the charac
	in that service. 

	Members:
		LSM_PRI_UUID -> UUID for the primary service.\n
		self.per -> copy of the peripheral class that we get from BTLE(This will be given while instantiating this class.)\n
		self.lsm_accelx_chrc ->Accelerometer X-axis characteristic.\n
		self.ksm_accelx_chrc_cccd -> Client Characterstic Configuration Descriptor for accelx chrc.\n
		self.lsm_accely_chrc ->Accelerometer Y-axis characteristic.\n
		self.ksm_accely_chrc_cccd -> Client Characterstic Configuration Descriptor for accely chrc.\n
		self.lsm_accelz_chrc ->Accelerometer Z-axis characteristic.\n
		self.ksm_accelz_chrc_cccd -> Client Characterstic Configuration Descriptor for accelz chrc.\n
		self.accelx_data -> Accelerometer X-axis characteristic data. \n
		self.accelx_is_fresh -> Current accelx chrc. value is fresh or not?\n
		self.accely_data -> Accelerometer Y-axis characteristic data. \n
		self.accely_is_fresh -> Current accely chrc. value is fresh or not?\n
		self.accelz_data -> Accelerometer Z-axis characteristic data. \n
		self.accelz_is_fresh -> Current accelz chrc. value is fresh or not?\n

	Methods:
		getService -> Get the primary service from the given peripheral. \n
		getCharacteristics -> Get the temp & hum. characteristics from the primary service.\n
		getCCCD -> Get the Client Characteristic Configuration Descriptors. \n
		enable_notification -> enable notifications for all chrcs.\n
		disable_notification -> disable notification for all chrcs.\n
		prepare_influx_data -> Once we have fresh data for all chrcs. prepare the data 
								in appropriate json format and send it to influxDB.\n
		configure -> Call all the above methods in proper sequence.\n
	'''

	# LSM_PRIM_UUID = 'e82bd800-c62c-43d5-b03f-c7381b38892a'
	# LSM_ACCELX_UUID = '461d287d-1ccd-46bf-8498-60139deeeb27'
	# LSM_ACCELY_UUID = 'a32f4917-d566-4273-b435-879eb85bd5cd'
	# LSM_ACCELZ_UUID = 'e6837dcc-ff0b-4329-a271-c3269c61b10d'
	CCCD_UUID = '2902'
	
	def __init__(self, periph, UUID='e82bd800-c62c-43d5-b03f-c7381b38892a',
								ACCELX_UUID='461d287d-1ccd-46bf-8498-60139deeeb27',
								ACCELY_UUID='a32f4917-d566-4273-b435-879eb85bd5cd',
								ACCELZ_UUID='e6837dcc-ff0b-4329-a271-c3269c61b10d'):
		self.LSM_PRIM_UUID = UUID
		self.LSM_ACCELX_UUID=ACCELX_UUID
		self.LSM_ACCELY_UUID=ACCELY_UUID
		self.LSM_ACCELZ_UUID=ACCELZ_UUID
		self.per = periph
		self.lsm_svc = None
		self.lsm_accelx_chrc = None
		self.lsm_accelx_chrc_cccd = None
		self.lsm_accely_chrc = None
		self.lsm_accely_chrc_cccd = None
		self.lsm_accelz_chrc = None
		self.lsm_accelz_chrc_cccd = None
		self.lsm_accelx_data=0
		self.lsm_accelx_is_fresh=False
		self.lsm_accely_data=0
		self.lsm_accely_is_fresh=False
		self.lsm_accelz_data=0
		self.lsm_accelz_is_fresh=False
		self.csv_file_name = "/home/dev/new/LSM/Local_LSM_Data.csv"
                
	def getService(self):
		self.lsm_svc = self.per.getServiceByUUID(self.LSM_PRIM_UUID)
        
	def getCharacteristics(self):
		self.lsm_accelx_chrc = self.lsm_svc.getCharacteristics(forUUID=self.LSM_ACCELX_UUID)[0]
		self.lsm_accely_chrc = self.lsm_svc.getCharacteristics(forUUID=self.LSM_ACCELY_UUID)[0]
		self.lsm_accelz_chrc = self.lsm_svc.getCharacteristics(forUUID=self.LSM_ACCELZ_UUID)[0]
	
	def getCCCD(self):
		self.lsm_accelx_chrc_cccd = self.lsm_accelx_chrc.getDescriptors(self.CCCD_UUID)[0]
		self.lsm_accely_chrc_cccd = self.lsm_accely_chrc.getDescriptors(self.CCCD_UUID)[0]
		self.lsm_accelz_chrc_cccd = self.lsm_accelz_chrc.getDescriptors(self.CCCD_UUID)[0]
		
	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
        
	def enable_notification(self):
		self.lsm_accelx_chrc_cccd.write(b"\x01\x00",True)
		self.lsm_accely_chrc_cccd.write(b"\x01\x00",True)
		self.lsm_accelz_chrc_cccd.write(b"\x01\x00",True)
	
                
	def disable_notification(self):  
		self.lsm_accelx_chrc_cccd.write(b"\x00\x00",False)
		self.lsm_accely_chrc_cccd.write(b"\x00\x00",False)
		self.lsm_accelz_chrc_cccd.write(b"\x00\x00",False)

	def open_csv_file(self):
		header = ["Time", "Board", "AccelX", "AccelY", "AccelZ"]
		if(os.path.exists(self.csv_file_name)):
			pass
		else:
			with open(self.csv_file_name, "w+") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(header)

	def append_csv_data(self, tag):
		time_t = time.ctime()
		data = [time_t, tag, self.lsm_accelx_data, self.lsm_accely_data, self.lsm_accelz_data]
		with open(self.csv_file_name, "a") as self.csv_fp:
			writer = csv.writer(self.csv_fp)
			writer.writerow(data)

	def prepare_influx_data(self, tag):
		iso = time.ctime()
		self.lsm_accelx_is_fresh=False
		self.lsm_accely_is_fresh=False
		self.lsm_accelz_is_fresh=False
		json_body = [
		{
			"measurement": "LSM",
			"time_t":iso,
			"tags":{
				"Board": tag,
				},
			"fields": {
				"AccelX": self.lsm_accelx_data,
				"AccelY": self.lsm_accely_data,
				"AccelZ": self.lsm_accelz_data,
				}
			}
		]
		write_influx_data(json_body)	
				
	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


class BMP_service():   
	'''
	Class for BMP280 Sensor on Adafruit Feather sense

	This class will be used for the BMP280 sensor on the adafruit feather sense board.
	It will match the UUID given in the primary service list and also get all the charac
	in that service. 

	Members:
		BMP_PRI_UUID -> UUID for the primary service.\n
		self.per -> copy of the peripheral class that we get from BTLE(This will be given while instantiating this class.)\n
		self.bmp_temp_chrc ->temperature characteristic.\n
		self.bmp_temp_chrc_cccd -> Client Characterstic Configuration Descriptor for temp. chrc.\n
		self.sht_press_chrc -> Pressure Characteristic \n
		self.sht_press_chrc_ccd -> Client Characterstic Configuration Descriptor for press. chrc.\n
		self.bmp_temp_data -> Temperature characteristic data. \n
		self.bmp_temp_is_fresh -> Current temp. chrc. value is fresh or not?\n
		self.bmp_press_data -> Pressure characteristic data.\n
		self.bmp_press_is_fresh -> Current press. chrc. value is fresh or not?\n

	Methods:
		getService -> Get the primary service from the given peripheral. \n
		getCharacteristics -> Get the temp & hum. characteristics from the primary service.\n
		getCCCD -> Get the Client Characteristic Configuration Descriptors. \n
		enable_notification -> enable notifications for all chrcs.\n
		disable_notification -> disable notification for all chrcs.\n
		prepare_influx_data -> Once we have fresh data for all chrcs. prepare the data 
								in appropriate json format and send it to influxDB.\n
		configure -> Call all the above methods in proper sequence.\n
	'''	   
	# BMP_PRI_UUID = 'f4356abe-b85f-47c7-ab4e-54df8f4ad025'
	BMP_TEMP_UUID = '2A6E'
	BMP_PRESS_UUID = '2A6D'  
	CCCD_UUID = '2902'

	def __init__(self, periph, UUID='f4356abe-b85f-47c7-ab4e-54df8f4ad025'):
		self.BMP_PRI_UUID=UUID
		self.per = periph
		self.bmp_svc = None
		self.bmp_temp_chrc = None
		self.bmp_temp_chrc_cccd = 0
		self.bmp_press_chrc = None
		self.bmp_press_chrc_cccd = 0
		self.bmp_temp_data = 0
		self.bmp_press_data=0
		self.bmp_temp_is_fresh = False
		self.bmp_press_is_fresh = False
		self.csv_file_name = "/home/dev/new/BMP/Local_BMP_Data.csv"
		
	def getService(self):
		self.bmp_svc = self.per.getServiceByUUID(self.BMP_PRI_UUID)
	
	def getCharacteristics(self):
		self.bmp_temp_chrc = self.bmp_svc.getCharacteristics(forUUID=self.BMP_TEMP_UUID)[0]
		# handle.append(self.sht_temp_chrc.valHandle)
		self.bmp_press_chrc = self.bmp_svc.getCharacteristics(forUUID=self.BMP_PRESS_UUID)[0]
		# print("the ValHandle for Pressure is: {}".format(self.bmp_press_chrc.valHandle))
		# handle.append(self.sht_hum_chrc.valHandle)
			
	def getCCCD(self):
		self.bmp_temp_chrc_cccd = self.bmp_temp_chrc.getDescriptors(self.CCCD_UUID)[0]
		self.bmp_press_chrc_cccd = self.bmp_press_chrc.getDescriptors(self.CCCD_UUID)[0]

	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
	
	def enable_notification(self):
		self.bmp_temp_chrc_cccd.write(b"\x01\x00",True)
		self.bmp_press_chrc_cccd.write(b"\x01\x00",True)

			
	def disable_notification(self):
		self.bmp_temp_chrc_cccd.write(b"\x00\x00",False)
		self.bmp_press_chrc_cccd.write(b"\x00\x00",False)    

	def check_data(self):
		''' sends message if the temperature value is non zero and also not in the rane [30-39]C.'''
		if(self.bmp_temp_data!=0 and (self.bmp_temp_data<=30.00 or self.bmp_temp_data>=39.00)):
			send_message("Critical Temperature Notified in BMP Sensor: {}".format(self.bmp_temp_data))

	def open_csv_file(self):
		header = ["Time", "Board", "Temperature", "Pressure"]
		if(os.path.exists(self.csv_file_name)):
			pass
		else:
			with open(self.csv_file_name, "w+") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(header)

	def append_csv_data(self,tag):
		time_t = time.ctime()
		data = [time_t, tag, self.bmp_temp_data, self.bmp_press_data]
		with open(self.csv_file_name, "a") as self.csv_fp:
			writer = csv.writer(self.csv_fp)
			writer.writerow(data)

	def prepare_influx_data(self, tag):
		self.check_data()
		iso = time.ctime()
		self.bmp_temp_is_fresh=False
		self.bmp_press_is_fresh=False
		json_body = [
		{
			"measurement": "BMP",
			"time_t":iso,
			"tags":{
				"Board": tag,
				},
			"fields": {
				"Temperature": self.bmp_temp_data,
				"pressure": self.bmp_press_data,
				}
			
			}
		]
		write_influx_data(json_body)

	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


class SCD_service(): 
	'''
	Class for SCD41 Sensor on Adafruit Feather sense

	This class will be used for the SCD41 sensor on the adafruit feather sense board.
	It will match the UUID given in the primary service list and also get all the charac
	in that service. 

	Members:
		BMP_PRI_UUID -> UUID for the primary service.\n
		self.per -> copy of the peripheral class that we get from BTLE(This will be given while instantiating this class.)\n
		self.scd_temp_chrc ->temperature characteristic.\n
		self.scd_temp_chrc_cccd -> Client Characterstic Configuration Descriptor for temp. chrc.\n
		self.scd_co2_chrc -> CO2 Characteristic \n
		self.scd_co2_chrc_ccd -> Client Characterstic Configuration Descriptor for CO2. chrc.\n
		self.scd_hum_chrc -> Humidity Characteristic \n
		self.scd_hum_chrc_ccd -> Client Characterstic Configuration Descriptor for hum. chrc.\n
		self.scd_temp_data -> Temperature characteristic data. \n
		self.scd_temp_is_fresh -> Current temp. chrc. value is fresh or not?\n
		self.scd_co2_data -> CO2 characteristic data.\n
		self.scd_co2_is_fresh -> Current CO2 chrc. value is fresh or not?\n
		self.scd_hum_data -> Hum characteristic data.\n
		self.scd_hum_is_fresh -> Current hum chrc. value is fresh or not?\n

	Methods:
		getService -> Get the primary service from the given peripheral. \n
		getCharacteristics -> Get the temp & hum. characteristics from the primary service.\n
		getCCCD -> Get the Client Characteristic Configuration Descriptors. \n
		enable_notification -> enable notifications for all chrcs.\n
		disable_notification -> disable notification for all chrcs.\n
		prepare_influx_data -> Once we have fresh data for all chrcs. prepare the data 
								in appropriate json format and send it to influxDB.\n
		configure -> Call all the above methods in proper sequence.\n
	'''		 

	# SCD_PRI_UUID = 'fb3047b4-df00-4eb3-9587-3b00e5bb5791'
	# SCD_CO2_UUID = 'b82febf7-93f8-93f8-8f52-b4797e33aab1'
	SCD_TEMP_UUID = '2A6E'
	SCD_HUM_UUID = '2A6F' 
	CCCD_UUID = '2902'

	def __init__(self, periph, UUID='fb3047b4-df00-4eb3-9587-3b00e5bb5791', 
								CO2_UUID='b82febf7-93f8-93f8-8f52-b4797e33aab1'):
		self.SCD_PRI_UUID=UUID
		self.SCD_CO2_UUID=CO2_UUID
		self.per = periph
		self.scd_svc = None
		self.scd_temp_chrc = None
		self.scd_temp_chrc_cccd = 0
		self.scd_hum_chrc = None
		self.scd_hum_chrc_cccd = 0
		self.scd_co2_chrc = None
		self.scd_co2_chrc_cccd = None
		self.scd_temp_data=0
		self.scd_hum_data=0
		self.scd_co2_data=0
		self.scd_temp_is_fresh=False
		self.scd_hum_is_fresh=False
		self.scd_co2_is_fresh=False
		self.csv_file_name = "/home/dev/new/SCD/Local_SCD_Data.csv"
			
	def getService(self):
		self.scd_svc = self.per.getServiceByUUID(self.SCD_PRI_UUID)
	
	def getCharacteristics(self):
		self.scd_temp_chrc = self.scd_svc.getCharacteristics(forUUID=self.SCD_TEMP_UUID)[0]
		self.scd_hum_chrc = self.scd_svc.getCharacteristics(forUUID=self.SCD_HUM_UUID)[0]
		self.scd_co2_chrc = self.scd_svc.getCharacteristics(forUUID=self.SCD_CO2_UUID)[0]
			
	def getCCCD(self):
		self.scd_temp_chrc_cccd = self.scd_temp_chrc.getDescriptors(self.CCCD_UUID)[0]
		self.scd_hum_chrc_cccd = self.scd_hum_chrc.getDescriptors(self.CCCD_UUID)[0]
		self.scd_co2_chrc_cccd = self.scd_co2_chrc.getDescriptors(self.CCCD_UUID)[0]

	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
	
	def enable_notification(self):
		self.scd_temp_chrc_cccd.write(b"\x01\x00",True)
		self.scd_hum_chrc_cccd.write(b"\x01\x00",True)
		self.scd_co2_chrc_cccd.write(b"\x01\x00", True)
	
			
	def disable_notification(self):
		self.scd_temp_chrc_cccd.write(b"\x00\x00",False)
		self.scd_hum_chrc_cccd.write(b"\x00\x00",False) 
		self.scd_co2_chrc_cccd.write(b"\x00\x00", False)   

	def check_data(self):
		if(self.scd_temp_data!=0 and (self.scd_temp_data<=30.00 or self.scd_temp_data>=39.00)):
			send_message("Critical Temperature Notified in SCD: {}".format(self.scd_temp_data))
		if(self.scd_hum_data!=0 and (self.scd_hum_data<=40.00 or self.scd_hum_data>=70.00)):
			send_message("Critical Humidity Notified in SCD: {}".format(self.scd_hum_data))

	def open_csv_file(self):
		header = ["Time", "Board", "Temperature", "Humidity", "Co2 Gas"]
		if(os.path.exists(self.csv_file_name)):
			pass
		else:
			with open(self.csv_file_name, "w+") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(header)

	def append_csv_data(self,tag):
		time_t = time.ctime()
		data = [time_t, tag, self.scd_temp_data, self.scd_hum_data, self.scd_co2_data]
		with open(self.csv_file_name, "a") as self.csv_fp:
			writer = csv.writer(self.csv_fp)
			writer.writerow(data)

	def prepare_influx_data(self, tag):
		self.check_data()
		iso = time.ctime()
		self.scd_co2_is_fresh=False
		self.scd_temp_is_fresh=False
		self.scd_hum_is_fresh=False
		json_body = [
        {
            "measurement": "SCD",
            "time_t":iso,
			"tags":{
				"Board": tag,
				},
            "fields": {
                "Temperature": self.scd_temp_data,
				"Humidity": self.scd_hum_data,
				"Gas": self.scd_co2_data,
            	}
            }
        ]
		write_influx_data(json_body)
			
	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()



class DS_service():  
	'''
	Class for DS18B20 Sensor on Adafruit Feather sense

	This class will be used for the DS18B20 sensor on the adafruit feather sense board.
	It will match the UUID given in the primary service list and also get all the charac
	in that service. 

	Members:
		BMP_PRI_UUID -> UUID for the primary service.\n
		self.per -> copy of the peripheral class that we get from BTLE(This will be given while instantiating this class.)\n
		self.ds_temp_chrcs[] -> list of temperature characteristic.\n
		self.ds_temp_chrc_cccds[] -> list of Client Characterstic Configuration Descriptor for temp. chrcs.\n
		self.ds_temp_datas[] -> list temperature characteristic data. \n
		self.ds_temp_is_fresh -> list of Current temp. chrc. values are fresh or not?\n

	Methods:
		getService -> Get the primary service from the given peripheral. \n
		getCharacteristics -> Get the temp & hum. characteristics from the primary service.\n
		getCCCD -> Get the Client Characteristic Configuration Descriptors. \n
		enable_notification -> enable notifications for all chrcs.\n
		disable_notification -> disable notification for all chrcs.\n
		prepare_influx_data -> Once we have fresh data for all chrcs. prepare the data 
								in appropriate json format and send it to influxDB.\n
		configure -> Call all the above methods in proper sequence.\n
	'''		

	# DS_PRI_UUID = '8121b46f-56ce-487f-9084-5330700681d5'
	DS_TEMP_UUID = '2A6E'
	CCCD_UUID = '2902'

	def __init__(self, periph, UUID,num_sensors=1):
		self.DS_PRI_UUID = UUID
		self.per = periph
		self.ds_svc = None
		self._num_sensors=num_sensors
		self.ds_temp_chrcs=[]
		self.ds_temp_chrc_cccds=[]
		self.ds_temp_datas=[0]*num_sensors
		self.ds_temp_is_fresh=[False]*num_sensors
		# One to One correspondence for the address and value.
		self.final_address_data = {'S1ULC':0.00, 'S1URC': 0.00, 'S1LLC':0.00, 'S1LRC':0.00, 
									'S2ULC': 0.00, 'S2URC': 0.00, 'S2LLC':0.00, 'S2LRC':0.00,
									'Outside': 0.00}
		self.csv_file_name_only_ds = "/home/dev/new/DS/Local_DS_Data_Only_DS_Board.csv"
		self.csv_file_name_all_sensor_board = "/home/dev/new/DS/Local_DS_Data_All_Sensor_Board.csv"


	def getService(self):
		self.ds_svc = self.per.getServiceByUUID(self.DS_PRI_UUID)
	
	def getCharacteristics(self):
		for ch in self.ds_svc.getCharacteristics(forUUID=self.DS_TEMP_UUID):
			self.ds_temp_chrcs.append(ch)
			
	def getCCCD(self):
		for c in self.ds_temp_chrcs:
			self.ds_temp_chrc_cccds.append(c.getDescriptors(self.CCCD_UUID)[0])

	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
	
	def enable_notification(self):
		for c in self.ds_temp_chrc_cccds:
			c.write(b"\x01\x00",True)
		
	def disable_notification(self):
		for c in self.ds_temp_chrc_cccds:
			c.write(b"\x01\x00",False)
		

	def put_data_in_appropriate_place(self,address, data):
		'''
		S1ULC: 0x1B
		S1URC: 0xD5
		S1LLC: 0X10
		S1LRC: 0X96
		S2ULC: 0xDC
		S2URC: 0x2B
		S2LLC: 0X2F
		S2LRC: 0XD2
		Out:   0x1D
		'''
		if address == 0x1B:
			self.final_address_data['S1ULC']=data
			return 0
		elif address == 0xD5:
			self.final_address_data['S1URC']=data
			return 1
		elif address == 0x10:
			self.final_address_data['S1LLC']=data
			return 2
		elif address == 0x96:
			self.final_address_data['S1LRC']=data
			return 3
		elif address == 0xDC:
			self.final_address_data['S2ULC']=data
			return 4
		elif address == 0x2B:
			self.final_address_data['S2URC']=data
			return 5
		elif address == 0x2F:
			self.final_address_data['S2LLC']=data
			return 6
		elif address == 0xD2:
			self.final_address_data['S2LRC']=data
			return 7
		elif address == 0x1D:
			self.final_address_data['Outside']=data
			return 8
		else:
			print("***We should not be here***")
			return -1

	def check_data(self):
		'''
		Method used to check all the temperature values and notify if the values are out of range
		'''
		# Code just for the outside DS sensors
		if (self._num_sensors!=1):
			for key, val in self.final_address_data.items():
				if(val!=0.00 and (val<=30.00 or val >=39.00)):
					send_message("Critical Temperature Notified in Only DS Sensor Board: "+"value: "+str(val)+"Pos: "+str(key))
		# For the inside board with just one sensor.
		else:
			if(self.ds_temp_datas[0]!=0.00 and (self.ds_temp_datas[0]<=30.00 or self.ds_temp_datas[0]>=39.00)):
				send_message("Critical Tempearture Notified in the All Sensor Board DS1: "+str(self.ds_temp_datas[0]))

	def open_csv_file(self):
		if(self._num_sensors==1):
			header1 = ["Time", "Board", "Temperature"]
		
			if(os.path.exists(self.csv_file_name_all_sensor_board)):
				pass
			else:
				with open(self.csv_file_name_all_sensor_board, "w+") as self.csv_fp:
					writer = csv.writer(self.csv_fp)
					writer.writerow(header1)

		elif(self._num_sensors==9):
			header2 = ["Time", "Board", "S1ULC(TEMP)", "S1URC(TEMP)", "S1LLC(TEMP)", "S1LRC(TEMP)", "S2ULC(TEMP)", "S2URC(TEMP)", "S2LLC(TEMP)", "S2LRC(TEMP)", "Outside(TEMP)"]
			if(os.path.exists(self.csv_file_name_only_ds)):
				pass
			else:
				with open(self.csv_file_name_only_ds, "w+") as self.csv_fp:
					writer = csv.writer(self.csv_fp)
					writer.writerow(header2)

	def append_csv_data(self,tag):
		time_t = time.ctime()
		# If statement for the all sensor board (Inner Board)
		if(self._num_sensors==1):
			data = [time_t, tag, self.ds_temp_datas[0]]
			with open(self.csv_file_name_all_sensor_board, "a") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(data)
		#Else if statement for the only DS Sensor Board(Outer Board)
		elif(self._num_sensors==9):
			data = [time_t, tag, self.final_address_data['S1ULC'], self.final_address_data['S1URC'], self.final_address_data['S1LLC'],
								self.final_address_data['S1LRC'], self.final_address_data['S2ULC'], self.final_address_data['S2URC'],
								self.final_address_data['S2LLC'], self.final_address_data['S2LRC'], self.final_address_data['Outside']]
			with open(self.csv_file_name_only_ds, "a") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(data)

	def prepare_influx_data(self, tag):
		# self.check_data()
		iso = time.ctime()
		for i in range(0, len(self.ds_temp_is_fresh)):
			self.ds_temp_is_fresh=False
		if(self._num_sensors==1):
			json_body = [
			{
				"measurement": "DS",
				"time_t":iso,
				"tags":{
					"Board": tag,
					},
				"fields": {
					"Temperature1": self.ds_temp_datas[0],
					}
				
				}
			]
		else:
			# print(self.final_address_data)
			# print("Normal:", self.ds_temp_datas)
			json_body = [
			{
				"measurement": "DS",
				"time_t":iso,
				"tags":{
					"Board": tag,
					},
				"fields": {
					"S1ULC": self.final_address_data['S1ULC'],
					"S1URC": self.final_address_data['S1URC'],
					"S1LLC": self.final_address_data['S1LLC'],
					"S1LRC": self.final_address_data['S1LRC'],
					"S2ULC": self.final_address_data['S2ULC'],
					"S2URC": self.final_address_data['S2URC'],
					"S2LLC": self.final_address_data['S2LLC'],
					"S2LRC": self.final_address_data['S2LRC'],
					"OUTSIDE": self.final_address_data['Outside'],
					}
				
				}
			]
		write_influx_data(json_body)
			
	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()

class Battery_service():
	CCCD_UUID='2902'
	def __init__(self,periph, UUID, BATTERY_VAL_UUID):
		self.per = periph
		self.BATT_UUID = UUID
		self.BATTERY_VAL_UUID=BATTERY_VAL_UUID
		self.battery_svc=None
		self.battery_chrc=None
		self.battery_chrc_cccd=0
		self.battery_data=0
		self.csv_file_name = "/home/dev/new/Battery/Local_Battery_Data.csv"

	def getService(self):
		self.battery_svc = self.per.getServiceByUUID(self.BATT_UUID)
	
	def getCharacteristics(self):
		self.battery_chrc = self.battery_svc.getCharacteristics(forUUID=self.BATTERY_VAL_UUID)[0]

	def getCCCD(self):
		self.battery_chrc_cccd = self.battery_chrc.getDescriptors(self.CCCD_UUID)[0]

	def enable_notification(self):
		self.battery_chrc_cccd.write(b"\x01\x00", True)
	
	def disable_notification(self):
		self.battery_chrc_cccd.write(b"\x00\x00", False)

	def open_csv_file(self):
		header = ["Time", "Board", "Battery Voltage"]
		if(os.path.exists(self.csv_file_name)):
			pass
		else:
			with open(self.csv_file_name, "w+") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(header)

	def append_csv_data(self,tag):
		time_t = time.ctime()
		data = [time_t, tag, self.battery_data]
		with open(self.csv_file_name, "a") as self.csv_fp:
			writer = csv.writer(self.csv_fp)
			writer.writerow(data)

	def prepare_influx_data(self,tag):
		iso = time.ctime()
		json_body = [
        {
            "measurement": "Battery",
            "time_t":iso,
			"tags":{
				"Board": tag,
				},
            "fields": {
                "Battery_Value": self.battery_data,
            	}            
            }
        ]
		write_influx_data(json_body)
	
	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


class BME_service(): 
	'''
	Class for BME680 Sensor on Adafruit Feather sense

	This class will be used for the BME680 sensor on the adafruit feather sense board.
	It will match the UUID given in the primary service list and also get all the charac
	in that service. 

	Members:
		BMP_PRI_UUID -> UUID for the primary service.\n
		self.per -> copy of the peripheral class that we get from BTLE(This will be given while instantiating this class.)\n
		self.bme_svc -> BME main service\n
		self.bme_tvoc_chrc -> TVOC characteristic\n
		self.bme_tvoc_chrc_cccd -> Client Characteristic Configuration Descriptor for TVOC chrc.\n
		self.bme_tvoc_data -> TVOC characteristic data\n

	Methods:
		getService -> Get the primary service from the given peripheral. \n
		getCharacteristics -> Get the temp & hum. characteristics from the primary service.\n
		getCCCD -> Get the Client Characteristic Configuration Descriptors. \n
		enable_notification -> enable notifications for all chrcs.\n
		disable_notification -> disable notification for all chrcs.\n
		prepare_influx_data -> Once we have fresh data for all chrcs. prepare the data 
								in appropriate json format and send it to influxDB.\n
		configure -> Call all the above methods in proper sequence.\n
	'''		 

	# BME_PRI_UUID = '54adba22-25c7-49d2-b4be-dbbb1a77efa3'
	# BME_TVOC_UUID = '67b2890f-e716-45e8-a8fe-4213db675224'
	CCCD_UUID = '2902'

	def __init__(self, periph, UUID='54adba22-25c7-49d2-b4be-dbbb1a77efa3', 
								TVOC_UUID='67b2890f-e716-45e8-a8fe-4213db675224'):
		self.BME_PRI_UUID=UUID
		self.BME_TVOC_UUID=TVOC_UUID
		self.per = periph
		self.bme_svc = None
		self.bme_tvoc_chrc = None
		self.bme_tvoc_chrc_cccd = None
		self.bme_tvoc_data=0
		self.csv_file_name = "/home/dev/new/BME/Local_BME_Data.csv"

	def getService(self):
		self.bme_svc = self.per.getServiceByUUID(self.BME_PRI_UUID)
	
	def getCharacteristics(self):
		self.bme_tvoc_chrc = self.bme_svc.getCharacteristics(forUUID=self.BME_TVOC_UUID)[0]
			
	def getCCCD(self):
		self.bme_tvoc_chrc_cccd = self.bme_tvoc_chrc.getDescriptors(self.CCCD_UUID)[0]

	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
	
	def enable_notification(self):
		self.bme_tvoc_chrc_cccd.write(b"\x01\x00", True)
	
			
	def disable_notification(self):
		self.bme_tvoc_chrc_cccd.write(b"\x00\x00", False)   

	def open_csv_file(self):
		header = ["Time", "Board", "TVOC_VALUE"]
		if(os.path.exists(self.csv_file_name)):
			pass
		else:
			with open(self.csv_file_name, "w+") as self.csv_fp:
				writer = csv.writer(self.csv_fp)
				writer.writerow(header)

	def append_csv_data(self,tag):
		time_t = time.ctime()
		data = [time_t, tag, self.bme_tvoc_data]
		with open(self.csv_file_name, "a") as self.csv_fp:
			writer = csv.writer(self.csv_fp)
			writer.writerow(data)

	def prepare_influx_data(self, tag):
		iso = time.ctime()
		json_body = [
        {
            "measurement": "BME",
            "time_t":iso,
			"tags":{
				"Board": tag,
				},
            "fields": {
				"TVOC_GAS": self.bme_tvoc_data,
            	}
            
            }
        ]
		write_influx_data(json_body)
			
	def configure(self):
		self.open_csv_file()
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


'''
# Try to make all the sensors into one shell and use it for each thread.
# Status: This will be a part of optimization so work on it after the deadline.
class All_Board_Sensor():
	def __init__(self, Address):
		# Call the connect peripheral method to get the peripheral class.
		self.per = self.connect_peripheral(Address=Address)
		self.SHT = SHT_service(periph=self.per)
		self.APDS = APDS_service(periph=self.per)
		self.BMP = BMP_service(periph=self.per)
		self.LSM = LSM_service(periph=self.per)
		self.SCD = SCD_service(periph=self.per)
		if(self.SCD is None):
			print("SCD is None type")
		self.DS = DS_service(periph=self.per, UUID='8121b46f-56ce-487f-9084-5330700681d5', num_sensors=1)
	
	# Configure all the sensor classes.
	def configure_all_sensors(self):
		self.SHT.configure()
		self.APDS.configure()
		self.BMP.configure()
		self.LSM.configure()
		self.DS	.configure()
		self.SCD.configure()

	# Call when first connected
	def enable_notifications(self):
		self.SHT.enable_notification()
		self.APDS.enable_notification()
		self.BMP.enable_notification()
		self.LSM.enable_notification()
		self.DS.enable_notification()
		self.SCD.enable_notification()
	
	# Call when reconnecting
	def enable_notifications(self, per):
		self.per=per
		self.SHT.enable_notification(self.per)
		self.APDS.enable_notification(self.per)
		self.BMP.enable_notification(self.per)
		self.LSM.enable_notification(self.per)
		self.DS.enable_notification(self.per)
		self.SCD.enable_notification(self.per)

	def disable_notifications(self):
		self.SHT.disable_notification()
		self.APDS.disable_notification()
		self.BMP.disable_notification()
		self.LSM.disable_notification()
		self.DS.disable_notification()
		self.SCD.disable_notification()


	# Class' notification delegate to call this everytime we get a notification for this peripheral
	

	def connect_peripheral(self, Address):
		print("All Board Sensor Class connecting to device {}...".format(Address))
		self.per = Peripheral(Address, ADDR_TYPE_RANDOM, iface=0)
		self.per.setDelegate(self.notifDelegate(outer=self))
		print("Successfully Connected to {} device\n".format(Address))
		return self.per
	
	# Disconnect the class' peripheral class
	def disconnect_peripheral(self):
		self.per.disconnect()
		time.sleep(2)
	
	def print_svcs(self):
		self.svc = self.per.getServices()
		for s in self.svc:
			self.ch = s.getCharacteristics()
			for c in self.ch:
				print(s.uuid, c)
'''




