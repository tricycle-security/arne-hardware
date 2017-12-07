#!/usr/bin/env python
# -*- coding: utf8 -*-

import signal
import os
import time
import RPi.GPIO as GPIO

from pirc522 import RFID

FACTORY_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
RUN = True

rdr = RFID()
util = rdr.util()
util.debug = True

def get_key_from_file(path):
  key = []
  with open(path, 'r') as key_file:
    data = key_file.readline()
    for char in data:
      key.append(ord(char))
  if(len(key) != 6):
    raise Exception("Invalid key: key must be 6 bytes long")
  else:
    return key

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global RUN
    print("\nCtrl+C captured, ending read.")
    RUN = False
    rdr.cleanup()
    GPIO.cleanup()
    raise Exception()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

print("Starting")
while RUN:
    rdr.wait_for_tag()

    (error, data) = rdr.request()
    # card is present and is a mifare card classic
    if not error and data == 16: 
        (error, uid) = rdr.anticoll()
        if not error:
            print("Card UID: " + str(uid[0]) + "," +str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3]))

            util.set_tag(uid)
            util.auth(rdr.auth_a, FACTORY_KEY)

            new_key = get_key_from_file('keyfile')
            
            for sector in range(15):
                print new_key


            util.deauth()
            RUN = False
        
