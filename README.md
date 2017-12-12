ARNE-hardware
=============
Attendance Recognition Notification Engine

## MFRC522-python

A small class to interface with the NFC reader Module MFRC522 on the Raspberry Pi.

This is a Python port of the example code for the NFC module MF522-AN.

## Requirements
Enable the SPI interfase in raspi-config.

This code requires you to have SPI-Py installed from the following repository:
https://github.com/lthiery/SPI-Py

## Sectors? Blocks?
Classic 1K MIFARE tag has **16 sectors**, each contains **4 blocks**. Each block has 16 bytes. All this stuff is indexed - you must count from zero. The library uses "**block addresses**", which are positions of blocks - so block address 5 is second block of second sector, thus it's block 1 of sector 1 (indexes). Block addresses 0, 1, 2, 3 are from the first sector - sector 0. Block addresses 4, 5, 6, 7 are from the second sector - sector 1, and so on. You should **not write** to first block - S0B0, because it contains manufacturer data. Each sector has it's **sector trailer**, which is located at it's last block - block 3. This block contains keys and access bits for corresponding sector. For more info, look at page 10 of the datasheet. You can use [this](http://www.proxmark.org/forum/viewtopic.php?id=1408) useful utility to calculate access bits.

## Pins
You can use [this](https://i.imgur.com/DRsymlo.png) image for reference. 

| Name | Pin # | Pin name      | Color |
|------|-------|---------------|-------|
| SDA  | 24    | GPIO8 - CE0   | Gray  |
| SCK  | 23    | GPIO11 - SCLK | Cherry|
| MOSI | 19    | GPIO10 - MOSI | Blue  |
| MISO | 21    | GPIO9 - MISO  | Green |
| IRQ  | 18    | GPIO24        | Yellow|
| GND  | 20    | GND           | Orange|
| RST  | 22    | GPIO25        | Red   |
| 3.3V | 17    | 3V3           | Brown |

## Usage
The library is split to two classes - **RFID** and **RFIDUtil**. You can use only RFID, RFIDUtil just makes life a little bit better.
You basically want to start with *while True* loop and "poll" the tag state. That's done using *request* method. Most of the methods
return error state, which is simple boolean - True is error, False is not error. The *request* method returns True if tag is **not**
present. If request is successful, you should call *anticoll* method. It runs anti-collision algorithms and returns used tag UID, which
you'll use for *select_tag* method. Now you can do whatever you want. Important methods are documented. You can also look at the Read and KeyChange examples for RFIDUtil usage.

```python
from pirc522 import RFID
rdr = RFID()

while True:
  rdr.wait_for_tag()
  (error, tag_type) = rdr.request()
  if not error:
    print("Tag detected")
    (error, uid) = rdr.anticoll()
    if not error:
      print("UID: " + str(uid))
      # Select Tag is required before Auth
      if not rdr.select_tag(uid):
        # Auth for block 10 (block 2 of sector 2) using default shipping key A
        if not rdr.card_auth(rdr.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid):
          # This will print something like (False, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
          print("Reading block 10: " + str(rdr.read(10)))
          # Always stop crypto1 when done working
          rdr.stop_crypto()

# Calls GPIO cleanup
rdr.cleanup()
```

### Util usage
**RFIDUtil** contains a few useful methods for dealing with tags.

```python
from pirc522 import RFID
import signal
import time

rdr = RFID()
util = rdr.util()
# Set util debug to true - it will print what's going on
util.debug = True

while True:
    # Wait for tag
    rdr.wait_for_tag()

    # Request tag
    (error, data) = rdr.request()
    if not error:
        print("\nDetected")

        (error, uid) = rdr.anticoll()
        if not error:
            # Print UID
            print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

            # Set tag as used in util. This will call RFID.select_tag(uid)
            util.set_tag(uid)
            # Save authorization info (key B) to util. It doesn't call RFID.card_auth(), that's called when needed
            util.auth(rdr.auth_b, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            # Print contents of block 4 in format "S1B0: [contents in decimal]". RFID.card_auth() will be called now
            util.read_out(4)
            # Print it again - now auth won't be called, because it doesn't have to be
            util.read_out(4)
            # Print contents of different block - S1B2 - RFID.card_auth() will be called again
            util.read_out(6)
            # We can change authorization info if you have different key in other sector
            util.auth(rdr.auth_a, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            #If you want to use methods from RFID itself, you can use this for authorization
            # This will authorize for block 1 of sector 2 -> block 9
            # This is once more called only if it's not already authorized for this block
            util.do_auth(util.block_addr(2, 1))
            # Now we can do some "lower-level" stuff with block 9
            rdr.write(9, [0x01, 0x23, 0x45, 0x67, 0x89, 0x98, 0x76, 0x54, 0x32, 0x10, 0x69, 0x27, 0x46, 0x66, 0x66, 0x64])
            # We can rewrite specific bytes in block using this method. None means "don't change this byte"
            # Note that this won't do authorization, because we've already called do_auth for block 9
            util.rewrite(9, [None, None, 0xAB, 0xCD, 0xEF])
            # This will write S2B1: [0x01, 0x23, 0xAB, 0xCD, 0xEF, 0x98, 0x76......] because we've rewritten third, fourth and fifth byte
            util.read_out(9)
            # Let's see what do we have in whole tag
            util.dump()
            # We must stop crypto
            util.deauth()
```