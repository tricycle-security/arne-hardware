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

# supress gpio warning messages to not flood stdout
# block where our data resides
# create rfid_adapter class
rfid = rfid_adapter.rfid_adapter()
# create rfid util class which makes helper function available
util = rfid.util()
# hook to SIGINT to execute the cleanup script
signal.signal(signal.SIGINT, rfid.end_read)
util.debug = True

# main loop
def main():
    while rfid.RUN:
        rfid.wait_for_tag()
        error, tag_type = rfid.request()
        if not error and tag_type == 16:
            error, uid = rfid.anticoll()
            if not error:
                error = util.set_tag(uid)
                if not error:
                    util.auth(rfid.auth_a, rfid.get_key_from_file('keyfile')[1])
                    error = util.rewrite(1, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                    if not error:
                        for sectors in range(16):
                            util.write_trailer(sectors)

        rfid.RUN = False

if __name__ == "__main__":
    main()
