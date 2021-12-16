from .prm_control_base import *

import pyfirmata

class PrMControlArduino(PrMControlBase):
    '''
    Controls the PrM via an arduino.
    '''

    def __init__(self, prm_id=1, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        super(PrMControlArduino, self).__init__(prm_id=prm_id, config=config)

        if 'arduino_address' not in config:
            raise PrMControlException(self._logger, 'Missing arduino_address in config.')

        self._logger.info(f"Trying to talk to Arduino at address {config['arduino_address']}")

        self._board = pyfirmata.Arduino(config['arduino_address'])

        self._logger.info(f"Connection established.")

        self._pin = 7

        self._logger.info('PrMControlArduino created.')


    def start_prm(self):
        '''
        Sets the parallel port pin that turns the HV ON.
        '''
        self._board.digital[self._pin].write(1)
        return


    def stop_prm(self):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        self._board.digital[self._pin].write(0)
        return