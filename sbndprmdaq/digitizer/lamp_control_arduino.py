'''
Contains class to control Arduino
'''

import logging
import pyfirmata


class LampControlArduino():
    '''
    Controls the flash lamp via an Arduino.
    '''

    def __init__(self, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''

        self._logger = logging.getLogger(__name__)

        #
        # Establish connection with the arduino
        #
        if 'arduino_address' not in config:
            raise ValueError(self._logger, 'Missing arduino_address in config.')

        self._logger.info(f"Trying to talk to Arduino at address {config['arduino_address']}")
        self._board = pyfirmata.Arduino(config['arduino_address'])
        self._logger.info("Connection with Arduino established.")

        #
        # Set the arduino GPIO pins
        #
        self._pin = None
        if 'arduino_pin' not in config:
            raise AttributeError(self._logger,
                                 'Missing arduino_pin in config.')
        self._pin = config['arduino_pin']
        self._board.digital[self._pin].write(0)
        self._logger.info("Arduino pins set to 0.")

        self._logger.info('LampControlArduino created.')


    def lamp_on(self):
        '''
        Turns on the lamp
        '''
        self._board.digital[self._pin].write(1)


    def lamp_off(self):
        '''
        Turns off the lamp
        '''
        self._board.digital[self._pin].write(0)


    def lamp_freq(self, freq):
        '''
        Sets the flashing frequency.
        '''
        self._logger.info(f'Setting frequency to {freq}.')
        self._logger.info('lamp_freq in LampControlArduino is not available.')
