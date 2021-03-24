import logging

class MockCommunicator():
    '''
    A mock class to simulate interaction with a parallel port.
    '''

    def __init__(self, port=0x0, prm_id=1):
        '''
        Constructor.

        Args:
            port: The port number.
            prm_id (int): The purity monitor ID.
        '''

        self._logger = logging.getLogger(__name__)
        self._logger.info('Fake parallel communicator created.')
        self._prm_id = prm_id
        return

    def start_prm(self):
        '''
        Sets the parallel port pin that turns the PrM ON.
        '''
        self._logger.info(f'Starting purity monitor {self._prm_id}.')

    def stop_prm(self):
        '''
        Sets the parallel port pin that turns the PrM OFF.
        '''
        self._logger.info(f'Stopping purity monitor {self._prm_id}.')

    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON.
        '''
        self._logger.info(f'HV set to ON for PrM ID {self._prm_id}.')

    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF.
        '''
        self._logger.info(f'HV set to OFF for PrM ID {self._prm_id}.')
