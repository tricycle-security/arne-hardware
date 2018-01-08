#!/usr/bin/env python3
# -*- coding: utf8 -*-

import random
import string
import rfid_adapter
import sys
import signal
from json import JSONEncoder

rfid = rfid_adapter.rfid_adapter()
util = rfid.util()

signal.signal(signal.SIGINT, rfid.end_read)

def main():
    banner()
    print("\nPlease place a factory fresh card infront of the RFID reader")
    print("\nKEEP THE CARD IN FRONT OF THE READER DURING THIS PROCESS")
    print("------------------------------------------------------------\n")
    while rfid.RUN:
        prepare_card()

def prepare_card():

    rfid.wait_for_tag()
    (request_error, tag_id) = rfid.request()

    if not request_error and tag_id == 16:
        (anticoll_error, uid) = rfid.anticoll()
        if not anticoll_error:
            select_error = util.set_tag(uid)
            if not select_error:
                # set key to factory default to check if card is fresh
                util.auth(rfid.auth_a, rfid.FACTORY_KEY)
                # force an authentication. If it fails card is not in factory state
                auth_error = util.do_auth(1, True)

                if not auth_error:
                    print("Generating unique user id\n-------------------------")
                    user_id = rfid.generate_userid()
                    print("User id is: {}".format(rfid.format_userid(user_id)))
                    
                    write_error = util.rewrite(1, user_id)
                    if not write_error:
                        print("Write successful! writen {} to card on S0B1\n".format(rfid.format_userid(user_id)))
                        read_error, data = rfid.read(1)
                        print(data)
                        if not read_error:
                            print("Reading back data unique user id: {}\n".format(rfid.format_userid(data)))                        

                            print("Writing keys to card\n-----------------------")
                            for block in range(16):
                                key_error = util.write_trailer(block, rfid.FACTORY_KEY, (0xFF, 0x07, 0x80), 0x42, rfid.FACTORY_KEY)
                                if not key_error:
                                    print("Written key to block {}".format(block))
                                else: 
                                    print("Key write failed for block {}".format(block))
                            if not key_error:
                                print("Changing auth key to new value")
                                util.auth(rfid.auth_a, rfid.FACTORY_KEY)
                                auth_error = util.do_auth(1)
                                
                                read_error, payload = rfid.read(1)
                                if not read_error and not auth_error:
                                   print(JSONEncoder().encode({"payload": rfid.format_userid(payload), "error": 0}))
                                else:
                                    print(JSONEncoder().encode({"payload": "failed", "error": 1}))
                        else:
                            print("Could not read back unique user id")
                    else:
                        print("Write failed! writen nothing to card")
                else:
                    print("Please provide a factory fresh card! and try again")
                    rfid.cleanup()
                    exit()

    rfid.RUN = False
    rfid.cleanup()



def write_userid(block):
    user_id = rfid.generate_userid
    error = util.rewrite(block, user_id)

    return error, user_id

def prompt_confirm():
    value = raw_input("Is this information correct?, [Y/N]: ")

    print(value)

def banner():
    print("""\n\
████████╗██████╗ ██╗ ██████╗██╗   ██╗ ██████╗██╗     ███████╗     ██████╗ █████╗ ██████╗ ██████╗     
╚══██╔══╝██╔══██╗██║██╔════╝╚██╗ ██╔╝██╔════╝██║     ██╔════╝    ██╔════╝██╔══██╗██╔══██╗██╔══██╗    
   ██║   ██████╔╝██║██║      ╚████╔╝ ██║     ██║     █████╗      ██║     ███████║██████╔╝██║  ██║    
   ██║   ██╔══██╗██║██║       ╚██╔╝  ██║     ██║     ██╔══╝      ██║     ██╔══██║██╔══██╗██║  ██║    
   ██║   ██║  ██║██║╚██████╗   ██║   ╚██████╗███████╗███████╗    ╚██████╗██║  ██║██║  ██║██████╔╝    
   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝   ╚═╝    ╚═════╝╚══════╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝     
                                                                                                     
██████╗ ██████╗ ███████╗██████╗  █████╗ ██████╗ ███████╗██████╗ ██╗                                  
██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██║                                  
██████╔╝██████╔╝█████╗  ██████╔╝███████║██████╔╝█████╗  ██████╔╝██║                                  
██╔═══╝ ██╔══██╗██╔══╝  ██╔═══╝ ██╔══██║██╔══██╗██╔══╝  ██╔══██╗╚═╝                                  
██║     ██║  ██║███████╗██║     ██║  ██║██║  ██║███████╗██║  ██║██╗                                  
╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝        
    """)

if __name__ == "__main__":
    main()
