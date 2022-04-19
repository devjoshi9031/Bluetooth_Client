#!/usr/bin/env python
import multiprocessing as mp
import time

event = None

def dummy():
    while(1):
        time.sleep(3)
        event.set()

def thread_creation(name):
    p = mp.Process(name = name, target=dummy)
    p.start()
    return p
if __name__ == "__main__":
    event = mp.Event()
    p = thread_creation("first")
    while True:
        if event.wait(2):
            print("True")
            event.clear()
        else:
            event.clear()
            p.terminate()
            p = thread_creation("current"+str(1))
            print("Created thread: {}".format("Current"+str(1)))

