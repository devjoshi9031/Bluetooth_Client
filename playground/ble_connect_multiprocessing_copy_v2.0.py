import multiprocessing as mp
import time, os, sys
from influxdb_client import Point

def post_processing_thread_fn(data_q):
    '''
    This thread will collect the data from a queue and depending on the internet availability, it will either send the data to the influxdb or save the data to the file.
    Steps:
    1. check for the value coming from the queue.
    2. check if internet is available.
    3. send the current data. 
    4. check if stale_data flag is high or not. If yes, read the file pointed by the file in the list and send everything to the influxdb and erase the file.
    5. if internet is not available, store the value in a file.
    6. do this in a while loop.
    '''
    # Dictonary to store the file names of all the sensors and also check if there is stale data available for a particular sensor file.
    file_status = {
        "SHT":["./SHT/Local_SHT_Data.csv",0],
        "SCD":["./SCD/Local_SCD_Data.csv",0],
        "LSM":["./LSM/Local_LSM_Data.csv",0],
        "BMP":["./BMP/Local_BMP_Data.csv",0],
        "BME":["./BME/Local_BME_Data.csv",0],
        "ONLY_DS":["./DS/Local_DS_Data_Only_DS_Board.csv",0],
        "All_DS":["./DS/Local_DS_Data_All_Sensor_Board.csv",0],
        "APDS":["./BME/Local_APDS_Data.csv",0],
    }
    print("Post processing thread entered while loop")
    while(1):
        time.sleep(1)
        try:
            # check if the data is available in the queue or not. 
            # If yes, go to the routine. Else, follow Except thing.
            data = data_q.get_nowait()
            print("Got data")
            if(data[0]=="SHT"):
                point = (
                    Point(data[0])
                    .field("Temperature", data[1])
                    .field("Humidity", data[2])
                    .time(time.ctime())
                )
            print("Prepared Point: {}".format(point))
            if(file_status[data[0]][1]==0):
                print("stale data not found")
        except Exception as e:
            # Do something. I don't know, just continue/pass?
            print(e)

def dummy_producer_thread_fn(data_q):
    data=[]
    print("Queue size: {}".format(data_q.qsize()))
    while(1):
        data.append("SHT")
        data.append(20.0)
        data.append(25.01)
        try:
            data_q.put(data)
        except:
            pass

def main():
    data_q = mp.Queue()
    p1 = mp.Process(target=dummy_producer_thread_fn, args=(data_q,))
    p2 = mp.Process(target=post_processing_thread_fn, args=(data_q,))
    # post_processing_thread_fn(data_q)
    p1.start()
    p2.start()
    p1.join()
    p2.join()



if __name__=='__main__':
    main()

    



