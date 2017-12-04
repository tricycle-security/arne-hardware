#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal

KEY_A = [] # TODO read from file and change to something else
KEY_B = []

continue_reading = True


# capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# welcome message
print "Welcome to the MFRC522 data read test"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID
# and authenticate
while continue_reading:

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # authenticate and read trailer blocks the data
        MIFAREReader.MFRC522_ReadTrailerBlock(MIFAREReader.PICC_AUTHENT1A, FACTORY_KEY, uid)

        # Stop
        MIFAREReader.MFRC522_StopCrypto1()


