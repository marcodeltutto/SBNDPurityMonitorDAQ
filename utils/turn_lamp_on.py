# Turns on the flash lamp

import pyfirmata

board = pyfirmata.Arduino(config['arduino_address'])
board.digital[pin].write(1)