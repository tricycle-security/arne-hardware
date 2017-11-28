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

## Pins
You can use [this](https://i.imgur.com/DRsymlo.png) image for reference.

| Name | Pin # | Pin name      | Color |
|------|-------|---------------|-------|
| SDA  | 24    | GPIO8 - CE0   | Gray  |
| SCK  | 23    | GPIO11 - SCLK | Cherry|
| MOSI | 19    | GPIO10 - MOSI | Blue  |
| MISO | 21    | GPIO9 - MISO  | Green |
| IRQ  | -     | -             | Yellow|
| GND  | 20    | GND           | Orange|
| RST  | 22    | GPIO25        | Red   |
| 3.3V | 17    | 3V3           | Brown |
