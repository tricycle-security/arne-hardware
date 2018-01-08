import sys
import random
import string
from pirc522 import RFID

class rfid_adapter(RFID):
    # GLOBALS
    FACTORY_KEY = (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
    RUN = True

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
    
    # capture SIGINT for cleanup when the script is aborted
    def end_read(self, signal, frame):
        """
        Cleans up the GPIO pins and exists the script gracefully
        """
        print("\nCtrl+C captured, ending read.")
        # call the cleanup function of the RFID instance created by initializing this class
        super(rfid_adapter, self).cleanup()
        raise Exception()
        
    def generate_userid(self):
        """
        Generated a pseudo-random userid to be written to card

        Returns a userid byte array
        """
        user_id = map(ord, ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for c in range(16)))
        return user_id

    def format_userid(self, userid_bytes):
        """
        Formats a user id byte array to a human readable string

        Returns user id string
        """
        string = ''.join(chr(byte) for byte in userid_bytes)

        return string
