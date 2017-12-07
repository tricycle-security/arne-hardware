#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import sys

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near it will get the UID
# and authenticate
while continue_reading:

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        # Get the UID of the card
        (status, uid) = MIFAREReader.MFRC522_Anticoll() # Method to get uid from cards in sequence

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Read the key after we selected the card by uid
        key = MIFAREReader.MFRC522_GetKeyFromFile("keyfile")
        
        # Authenticate to the selected tag
        authStatus = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 1, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid)
        
        # Read block 1 from selected card
        if authStatus == MIFAREReader.MI_OK:
            sector, data = MIFAREReader.MFRC522_Read(1)
            payload = ''.join(chr(integer) for integer in data)
            
        print payload # Sending data to Nodejs
        sys.stdout.flush() # Clearing the stdout buffer to be ready for the next message

        # Stop
        MIFAREReader.MFRC522_StopCrypto1()
        time.sleep(2) # For now we use a timeout to not flood the Nodejs application. THIS SHOULD BE FIXED
