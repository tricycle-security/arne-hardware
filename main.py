#!/usr/bin/env python3
# -*- coding: utf8 -*-

import argparse
import signal
import sys
import rfid_adapter
import random
import string
import time
import RPi.GPIO as GPIO
from json import JSONEncoder

# block where our data resides
BLOCK = 1
CURRENT_SCAN_TIME = None
CURRENT_CARD = None
# create rfid_adapter class
rfid = rfid_adapter.rfid_adapter()
# create rfid util class which makes helper function available
util = rfid.util()
# hook to SIGINT to execute the cleanup script
signal.signal(signal.SIGINT, rfid.end_read)


# main loop
def main():
    while rfid.RUN:
        emit_userid()


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
                else:
                    print(JSONEncoder().encode({"payload": "No authentication", "error": 1}))
                    sys.stdout.flush()

    elif tag_type is not None:
        print(JSONEncoder().encode({"payload": "Unknown card", "error": 1}))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
