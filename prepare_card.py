#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import random
import string

CONTINUE_READING = True
# the key cards have from when they come on from the factory
FACTORY_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
# generate a pseudo random 16 byte alphanumeric user id
USER_ID = map(ord, ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for c in range(16)))

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global CONTINUE_READING
    print "Ctrl+C captured, ending read."
    CONTINUE_READING = False
    GPIO.cleanup()

# hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# welcome message
print "Welcome to the Tricycle Security card preparer..."
print "Press Ctrl-C to stop."

while CONTINUE_READING:

    # scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # if a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # if we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # print UID
        print "Card read UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])

        # select the scanned card
        MIFAREReader.MFRC522_SelectTag(uid)

        # Write user id to sector 0 using factory key
        MIFAREReader.MFRC522_AuthedWrite(MIFAREReader.PICC_AUTHENT1A, FACTORY_KEY, 1, USER_ID, uid)
        
        # get the key to write from the keyfile
        new_key = MIFAREReader.MFRC522_GetKeyFromFile("keyfile")

        # authenticate and write key to trailer blocks
        MIFAREReader.MFRC522_WriteNewKey(MIFAREReader.PICC_AUTHENT1A, FACTORY_KEY, new_key, uid)
        
        # stop and done
        MIFAREReader.MFRC522_StopCrypto1()
        
        CONTINUE_READING = False
