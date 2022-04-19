from concurrent.futures import thread
import threading
import logging as log
import time
def dummy():
    while(1):
        log.info("Hello from the {} thread".format(threading.current_thread().name))
        print("Hello from the {} thread".format(threading.current_thread().name))
        time.sleep(10)
        if stop_thread:
            break
        event.set()

event = threading.Event()
stop_thread = False
if __name__ == "__main__":
    format = "%(asctime)s.%(msecs)03d: %(message)s"
    log.basicConfig(filename="logfile.log", 
                        filemode = "a",
                            format=format, level=log.INFO,
                                datefmt="%H:%M:%S")
    
    log.info("{} : before creating thread".format(threading.current_thread().name))
    print("{} : before creating thread".format(threading.current_thread().name))
    t = threading.Thread(target=dummy, name="Dev")
    t.start()
    time.sleep(1)
    flag = event.wait(5.0)
    if ~flag:
        print("thread didn't came back! destroying thread!")
        stop_thread=True    

    log.error("Wait returned with {}".format(flag))
    log.info("{}: Thread created successfully".format(threading.current_thread().name))
    print("{}: Thread created successfully".format(threading.current_thread().name))

    