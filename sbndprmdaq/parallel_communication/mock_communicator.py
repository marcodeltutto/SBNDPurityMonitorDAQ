import logging

class MockCommunicator():

    def __init__(self, port=0x0):

        self._logger = logging.getLogger(__name__)
        self._logger.info('Fake parallel communicator created.')
        return

    def start_prm(self):
        self._logger.info('Starting purity monitor.')

    def stop_prm(self):
        self._logger.info('Stopping purity monitor.')

    def hv_on(self):
        self._logger.info('HV set to ON.')

    def hv_off(self):
        self._logger.info('HV set to OFF.')
