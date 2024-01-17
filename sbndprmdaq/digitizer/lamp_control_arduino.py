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

        if 'disable_arduino' not in config:
            raise ValueError(self._logger, 'Missing disable_arduino in config.')

        self._logger.info(f"Trying to talk to Arduino at address {config['arduino_address']}")
        if not config['disable_arduino']:
            self._board = pyfirmata.Arduino(config['arduino_address'])
        else:
            self._board = None

        self._logger.info("Connection with Arduino established.")

        #
        # Set the arduino GPIO pins
        #
        self._pin = None
        if 'arduino_pin' not in config:
            raise AttributeError(self._logger,
                                 'Missing arduino_pin in config.')
        self._pin = config['arduino_pin']
        if self._board is not None:
            self._board.digital[self._pin].write(0)
        self._logger.info("Arduino pins set to 0.")

        self._logger.info('LampControlArduino created.')


    def lamp_on(self):
        '''
        Turns on the lamp
        '''
        if self._board is not None:
            self._board.digital[self._pin].write(1)
        else:
            self._logger.info('lamp_on.')



    def lamp_off(self):
        '''
        Turns off the lamp
        '''
        if self._board is not None:
            self._board.digital[self._pin].write(0)
        else:
            self._logger.info('lamp_off.')


    def lamp_freq(self, freq):
        '''
        Sets the flashing frequency.
        '''
        self._logger.info(f'Setting frequency to {freq}.')
        self._logger.info('lamp_freq in LampControlArduino is not available.')
