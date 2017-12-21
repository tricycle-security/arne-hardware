#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import random
import string
import rfid_adapter

# the key cards have from when they come on from the factory
FACTORY_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# create rfid_adapter class
rfid = rfid_adapter.rfid_adapter()
# create rfid util class which makes helper function available
util = rfid.util()
util.debug = False
    
while rfid.RUN:
    print("Please place a card in front of the reader")
    rfid.wait_for_tag()
    (error, data) = rfid.request()
    if not error and data == 16:
        (error, uid) = rfid.anticoll()
        if not error:
            # set the uid for the card we are working with
            util.set_tag(uid)
            # set the auth key for the current selected card with the factory
            # key
            util.auth(rfid.auth_a, (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF))
            util.dump()
            rfid.RUN = False
