CCCD_UUID = '2902'
        
'''
handle[0] = sht_temp
handle[1] = sht_hum
handle[2] = apds_prox
handle[3] = apds_red
handle[4] = apds_blue
handle[5] = apds_green
handle[6] = apds_clear
handle[7] = lsm_accel_x
handle[8] = lsm_accel_y
handle[9] = lsm_accel_z
handle[10] = lsm_gyrox
handle[11] = lsm_gyroy
handle[12] = lsm_gyroz
handle[13] = scd_co2
handle[14] = scd_temp
handle[15] = scd_hum
handle[16] = ds_temp

'''
handle = []

def print_handle():
	print("Inside print handle method\n")
	for i in handle:
		print(i) 

class SHT_service():      
	SHT_PRI_UUID = '57812a99-9146-4e72-a4b7-5159632dee90'
	SHT_TEMP_UUID = '2A6E'
	SHT_HUM_UUID = '2A6F'  
	CCCD_UUID = '2902'
	
	def __init__(self, periph):
		self.per = periph
		self.sht_svc = None
		self.sht_temp_chrc = None
		self.sht_temp_chrc_cccd = 0
		self.sht_hum_chrc = None
		self.sht_hum_chrc_cccd = 0
		self.tempisfresh = False
		self.humisfresh = False
		self.sht_temp_data=0
		self.sht_hum_data=0
			
	def getService(self):
		self.sht_svc = self.per.getServiceByUUID(self.SHT_PRI_UUID)
	
	def getCharacteristics(self):
		self.sht_temp_chrc = self.sht_svc.getCharacteristics(forUUID=self.SHT_TEMP_UUID)[0]
		handle.append(self.sht_temp_chrc.valHandle)
		self.sht_hum_chrc = self.sht_svc.getCharacteristics(forUUID=self.SHT_HUM_UUID)[0]
		handle.append(self.sht_hum_chrc.valHandle)
			
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
			
	def configure(self):
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


class APDS_service():
	APDS_PRI_UUID = 'ebcc60b7-974c-43e1-a973-426e79f9bc6c'
	APDS_CLEAR_UUID = 'e960c9b7-e0ed-441e-b22c-d93252fa0fc6'
	CCCD_UUID = '2902'
	
	def __init__(self, periph):
		self.per = periph
		self.apds_svc = None
		self.apds_clear_chrc = None
		self.apds_clear_chrc_cccd = 0
		self.apds_clear_data=0
			
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
                
	def configure(self):
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()
	def getHandle(self):
		print(self.apds_clear_chrc.valHandle)
			
	
class LSM_service():
	LSM_PRIM_UUID = 'e82bd800-c62c-43d5-b03f-c7381b38892a'
	LSM_ACCELX_UUID = '461d287d-1ccd-46bf-8498-60139deeeb27'
	LSM_ACCELY_UUID = 'a32f4917-d566-4273-b435-879eb85bd5cd'
	LSM_ACCELZ_UUID = 'e6837dcc-ff0b-4329-a271-c3269c61b10d'
	CCCD_UUID = '2902'
	
	def __init__(self, periph):
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
			
	def configure(self):
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()
	def getHandle(self):
		print(self.lsm_accelx_chrc.valHandle)
		print(self.lsm_accely_chrc.valHandle)
		print(self.lsm_accelz_chrc.valHandle)


class BMP_service():      
	BMP_PRI_UUID = 'f4356abe-b85f-47c7-ab4e-54df8f4ad025'
	BMP_TEMP_UUID = '2A6E'
	BMP_PRESS_UUID = '2A6D'  
	CCCD_UUID = '2902'

	def __init__(self, periph):
		self.per = periph
		self.bmp_svc = None
		self.bmp_temp_chrc = None
		self.bmp_temp_chrc_cccd = 0
		self.bmp_press_chrc = None
		self.bmp_press_chrc_cccd = 0
		self.bmp_temp_data = 0
		self.bmp_press_data=0
		self.tempisfresh = False
		self.pressisfresh = False
		
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
			
	def configure(self):
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()


class SCD_service():  

	SCD_PRI_UUID = 'fb3047b4-df00-4eb3-9587-3b00e5bb5791'
	SCD_CO2_UUID = 'b82febf7-93f8-93f8-8f52-b4797e33aab1'
	SCD_TEMP_UUID = '2A6E'
	SCD_HUM_UUID = '2A6F' 
	CCCD_UUID = '2902'

	def __init__(self, periph):
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
			
	def getService(self):
		self.scd_svc = self.per.getServiceByUUID(self.SCD_PRI_UUID)
	
	def getCharacteristics(self):
		self.scd_temp_chrc = self.scd_svc.getCharacteristics(forUUID=self.SCD_TEMP_UUID)[0]
			# handle.append(self.sht_temp_chrc.valHandle)
		self.scd_hum_chrc = self.scd_svc.getCharacteristics(forUUID=self.SCD_HUM_UUID)[0]
			# handle.append(self.sht_hum_chrc.valHandle)
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
			
	def configure(self):
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()




class DS_service():  

	DS_PRI_UUID = '8121b46f-56ce-487f-9084-5330700681d5'
	DS_TEMP_UUID = '2A6E'

	CCCD_UUID = '2902'

	def __init__(self, periph):
		self.per = periph
		self.ds_svc = None
		self.ds_temp_chrc = None
		self.ds_temp_chrc_cccd = 0
		self.ds_temp_data=0
		self.ds_temp_is_fresh=False
			
	def getService(self):
		self.ds_svc = self.per.getServiceByUUID(self.DS_PRI_UUID)
	
	def getCharacteristics(self):
		self.ds_temp_chrc = self.ds_svc.getCharacteristics(forUUID=self.DS_TEMP_UUID)[0]
			# handle.append(self.sht_temp_chrc.valHandle)
			
	def getCCCD(self):
		self.ds_temp_chrc_cccd = self.ds_temp_chrc.getDescriptors(self.CCCD_UUID)[0]

	def getServicebyUUID(self,uuid):
		return self.per.getServicebyUUID(uuid)
	
	def enable_notification(self):
		self.ds_temp_chrc_cccd.write(b"\x01\x00",True)
	
			
	def disable_notification(self):
		self.ds_temp_chrc_cccd.write(b"\x00\x00",False)
			
	def configure(self):
		self.getService()
		self.getCharacteristics()
		self.getCCCD()
		self.enable_notification()