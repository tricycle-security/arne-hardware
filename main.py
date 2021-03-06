#!/usr/bin/env python3
# -*- coding: utf8 -*-

import signal
import sys
import rfid_adapter
import string
import time
import RPi.GPIO as GPIO
from json import JSONEncoder

BLOCK = 1
CURRENT_SCAN_TIME = None
CURRENT_CARD = None
BUZZER_PIN = 12  # set the buzzer pin variable to number 11
CARDS = []
# create rfid_adapter class
rfid = rfid_adapter.rfid_adapter()
# create rfid util class which makes helper function available
util = rfid.util()
# setup gpio pins for buzzer
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# hook to SIGINT to execute the cleanup script
signal.signal(signal.SIGINT, rfid.end_read)


# main loop
def main():
    while rfid.RUN:
        emit_userid()


def buzz(pitch, duration):
    """
    Makes noise with the provided pitch and duration
    """  
    # create the function "buzz" and feed it the pitch and duration)
    # in physics, the period (sec/cyc) is the inverse of the frequency
    # (cyc/sec)
    period = 1.0 / pitch
    delay = period / 2  # calcuate the time for half of the wave
    # the number of waves to produce is the duration times the frequency
    cycles = int(duration * pitch)

    for i in range(cycles):  # start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(BUZZER_PIN, True)  # set pin 18 to high
        time.sleep(delay)  # wait with pin 18 high
        GPIO.output(BUZZER_PIN, False)  # set pin 18 to low
        time.sleep(delay)  # wait with pin 18 low

def emit_userid():
    """
    Tries to authenticate to a scanned card and emit its contents for further prosessing

    Emits error state and message
    """
    global CURRENT_CARD
    global CURRENT_SCAN_TIME
    # wait for a rfid tag event to continue the loop
    rfid.wait_for_tag()
    # request tag type from tag
    (error, tag_type) = rfid.request()
    # if tag is present and is a mifare card
    if not error and tag_type == 16:
        # get the uid of the tag
        (error, uid) = rfid.anticoll() # a method to get uid from cards in sequence
        if not error and (CURRENT_CARD != uid or (time.time() - CURRENT_SCAN_TIME > 5)):            
            # set globals for card timeout
            CURRENT_CARD = uid
            CURRENT_SCAN_TIME = time.time()

            # select tag to use for authentication 
            if not rfid.select_tag(uid):
                # retrieve authentication key from file
                error, key = rfid.get_key_from_file('keyfile')
                # authenticate to block with key
                if not error and not rfid.card_auth(rfid.auth_a, BLOCK, key, uid):
                    (error, data) = rfid.read(BLOCK)
                    if not error:
                        payload = ''.join(chr(integer) for integer in data)
                        output = JSONEncoder().encode({"payload": payload, "error": 0})
                        print(output)
                        sys.stdout.flush()  # clearing the stdout buffer to be ready for the next message      
                        rfid.stop_crypto()  # deauthenticate the card and clear keys
                        
                        if output in CARDS:
                            buzz(800, 0.3) # check out sound
                            CARDS.remove(output)
                        else:
                            buzz(1500, 0.3) # check in sound
                            CARDS.append(output)
                else:
                    print(JSONEncoder().encode({"payload": "No authentication", "error": 1}))
                    sys.stdout.flush()

    elif tag_type is not None:
        print(JSONEncoder().encode({"payload": "Unknown card", "error": 1}))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
