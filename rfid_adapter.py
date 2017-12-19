import sys
import string
import random
import time
import RPi.GPIO as GPIO
from pirc522 import RFID
from json import JSONEncoder

class rfid_adapter(RFID):
    # GLOBALS
    RUN = True
    FACTORY_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    BLOCK = 1
    CURRENT_SCAN_TIME = None
    CURRENT_CARD = None
    EVENT = False

    # capture SIGINT for cleanup when the script is aborted
    def end_read(self, signal, frame):
        """
        Cleans up the GPIO pins and exists the script gracefully
        """
        print("\nCtrl+C captured, ending read.")
        # call the cleanup function of the RFID instance created by initializing this class
        super(rfid_adapter, self).cleanup()
        raise Exception()

    def emit_userid(self):
        """
        Tries to authenticate to a scanned card and emit its contents for further prosessing

        Emits error state and message
        """
        # wait for a rfid tag event to continue the loop
        self.super().wait_for_tag()
        # request tag type from tag
        (error, tag_type) = self.super().request()
        # if tag is present and is a mifare card
        if not error and tag_type == 16:
            # get the uid of the tag
            # a method to get uid from cards in sequence
            (error, uid) = self.super().anticoll()
            if not error and (self.CURRENT_CARD != uid or (time.time() - self.CURRENT_SCAN_TIME > 5)):
                # set globals for card timeout
                self.CURRENT_CARD = uid
                self.CURRENT_SCAN_TIME = time.time()

                # select tag to use for authentication
                if not self.super().select_tag(uid):
                    # retrieve authentication key from file
                    error, key = self.get_key_from_file('keyfile')
                    # authenticate to block with key
                    if not error and not self.super().card_auth(self.super().auth_a, self.BLOCK, key, uid):
                        (error, data) = self.super().read(self.BLOCK)
                        if not error:
                            payload = ''.join(chr(integer) for integer in data)
                            output = JSONEncoder().encode({"payload": payload, "error": 0})
                            return output
                            self.super().stop_crypto()  # deauthenticate the card and clear keys
                    else:
                        return JSONEncoder().encode({"payload": "noauth", "error": 1})

        elif tag_type is not None:
            return JSONEncoder().encode({"payload": "unknowncard", "error": 1})

    def generate_userid(self):
        """
        Generated a pseudo-random userid to be written to card

        Returns a userid byte array
        """
        user_id = map(ord, ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for c in range(16)))
        return user_id
    
    def get_key_from_file(self, path):
        """
        Gets the contents of the given file and tries to encode this into a byte / litteral array
        path -- string path to file to read key from
        Returns error state and key
        """
        key = []
        error = False
        with open(path, 'r') as key_file:
            data = key_file.readline()
            for char in data:
                key.append(ord(char))
        if(len(key) != 6):
            error = True
            return (error, tuple(key))
        else:
            return (error, tuple(key))

    def super(self):
        return super(rfid_adapter, self)
