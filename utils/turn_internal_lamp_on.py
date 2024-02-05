#!/usr/bin/env python3

# Turns on the flash lamp

import pyfirmata

board = pyfirmata.Arduino('/dev/arduino')
board.digital[7].write(1)
