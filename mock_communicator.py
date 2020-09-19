import logging

class MockCommunicator():

    def __init__(self, port=0x0):

        logger = logging.getLogger(__name__)
        logger.info('Fake parallel communicator created.')
        return

    def start_prm(self):
        print('PrM started')

    def stop_prm(self):
        print('PrM stopped')

    def hv_on(self):
        print('HV ON')

    def hv_off(self):
        print('HV OFF')
