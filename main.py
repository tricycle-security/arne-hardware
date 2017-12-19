#!/usr/bin/env python3
# -*- coding: utf8 -*-

import argparse
import signal
import rfid_adapter

# create rfid_adapter class
rfid = rfid_adapter.rfid_adapter()
# create rfid util class which makes helper function available
util = rfid.util()
# hook to SIGINT to execute the cleanup script
signal.signal(signal.SIGINT, rfid.end_read)

def parse_args():
    # store commandline arguments
    parser = argparse.ArgumentParser(description='Trycicle security RFID card reader and preparer')
    parser.add_argument('-p', '--prepare', action='store_true', help='Prepare cards with custom key')
    args = parser.parse_args()

    return args

# main loop
def main():
    args = parse_args()

    if args.prepare:
        while rfid.RUN:
            prepare_card()
    elif not args.prepare:
        while rfid.RUN:
            output = rfid.emit_userid()
            if output is not None:
                print(output)
    else:
        exit()

def prepare_card():
    """
    Prepares a card in factory state to be used in the production environment with a given keyfile
    """
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
            # generate a pseudo-random userid
            user_id = generate_userid()
            # write the userid to our block
            util.rewrite(BLOCK, user_id)
            # get the key from the keyfile
            error, new_key = rfid.get_key_from_file('keyfile')
            # change key for every trailer block
            if not error and new_key is not None:
                for sector in range(15):
                    print("Writing key to sector: " + str(sector))
                    util.write_trailer(sector, new_key, (0xFF, 0x07, 0x80), 0x69, new_key)
            else:
                print("Could not get key from file")
            util.deauth()
            rfid.RUN = False

if __name__ == "__main__":
    main()
