#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import signal
import sys
import rfid_adapter

# store commandline arguments
parser = argparse.ArgumentParser(description='Trycicle security RFID card reader and preparer')
required = parser.add_argument_group('required argument(s) choose one')
optional = parser.add_argument_group('optional arguments')
required.add_argument('-r', '--read', action='store_true', help='Read RFID Mifare Classic cards')
required.add_argument('-p', '--prepare', action='store_true', help='Prepare cards with custom key')
args = parser.parse_args()
# sector where our data resides
SECTOR_TO_READ = 1
# create rfid_adapter class
rfid = rfid_adapter.rfid_adapter()
# create rfid util class which makes helper function available
util = rfid.util()

# hook to SIGINT to execute the cleanup script
signal.signal(signal.SIGINT, rfid.end_read)

# main loop
def main(argv):
    if args.read and args.prepare:
        print("Please provide one argument!")
        exit()
    if args.read:
        while rfid.RUN:
            emit_userid()
    if args.prepare:
        while rfid.RUN:
            prepare_card()

def emit_userid():
    """
    Tries to authenticate to a scanned card and emit its contents for further prosessing

    Returns userid
    """
    # wait for a rfid tag event to continue the loop
    rfid.wait_for_tag()
    # request tag type from tag
    (error, tag_type) = rfid.request()
    # if tag is present and is a mifare card
    if not error and tag_type == 16:
        # get the uid of the tag
        (error, uid) = rfid.anticoll() # a method to get uid from cards in sequence
        if not error:
            # select tag to use for authentication
            if not rfid.select_tag(uid):
                # retrieve authentication key from file
                error, key = rfid.get_key_from_file('keyfile')
                # authenticate to block 1 with key
                if not error and not rfid.card_auth(rfid.auth_a, SECTOR_TO_READ, key, uid):
                    (error, data) = rfid.read(SECTOR_TO_READ)
                    if not error:
                        payload = ''.join(chr(integer) for integer in data)
                        print payload # send user id to node via stdout
                        sys.stdout.flush()  # clearing the stdout buffer to be ready for the next message
                rfid.stop_crypto()  # deauthenticate the card and clear keys

def prepare_card():
    """
    Prepares a card in factory state to be used in the production environment with a given keyfile
    """
    util.debug = True
    print("Please place a clean card in front of the reader")
    # wait for a rfid tag event to continue the loop
    rfid.wait_for_tag()
    # request tag type from tag 
    (error, data) = rfid.request()
    # if tag is present and is a mifare card
    if not error and data == 16:
        # get the uid of the tag
        # a method to get uid from cards in sequence
        (error, uid) = rfid.anticoll()
        if not error:
            # set the uid for the card we are working with
            util.set_tag(uid)
            # set the auth key for the current selected card with the factory key
            util.auth(rfid.auth_a, (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF))
            
            # get the key from the keyfile
            error, new_key = rfid.get_key_from_file('keyfile')
            # change key for every trailer block
            if not error and new_key is not None:
                for sector in range(15):
                    print("Writing key to sector: "+str(sector))
                    #util.write_trailer(sector, new_key, (0xFF, 0x07, 0x80), 0x69, new_key)
            else:
                print("Could not get key from file")
            util.deauth()
            rfid.RUN = False

if __name__ == "__main__":
    main(sys.argv)