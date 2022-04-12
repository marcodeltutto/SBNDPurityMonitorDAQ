from .prm_control_base import *

import pyfirmata

class PrMControlArduino(PrMControlBase):
    '''
    Controls the PrM via an arduino.
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        super(PrMControlArduino, self).__init__(prm_ids=prm_ids, config=config)

        #
        # Establish connection with the arduino
        #
        if 'arduino_address' not in config:
            raise PrMControlException(self._logger, 'Missing arduino_address in config.')

        self._configure()

        self._logger.info('PrMControlArduino created.')

    def _configure(self):

        self._logger.info(f"Trying to talk to Arduino at address {config['arduino_address']}")
        self._board = pyfirmata.Arduino(config['arduino_address'])
        self._logger.info(f"Connection with Arduino established.")

        #
        # Set the arduino GPIO pins
        #
        self._pins = {}
        for prm_id in prm_ids:
            if f'arduino_prm{prm_id}_pin' not in config:
                raise PrMControlException(self._logger,
                                          f'Missing arduino_prm{prm_id}_pin in config.')
            else:
                self._pins[prm_id] = config[f'arduino_prm{prm_id}_pin']
                self._board.digital[self._pins[prm_id]].write(0)
        self._logger.info("Arduino pins set to 0.")


    def start_prm(self, prm_id=1):
        '''
        Starts the PrM.
        '''
        pin = self._pins[prm_id]
        self._board.digital[pin].write(1)
        return


    def stop_prm(self, prm_id=1):
        '''
        Stops the PrM.
        '''
        pin = self._pins[prm_id]
        self._board.digital[pin].write(0)
        return
