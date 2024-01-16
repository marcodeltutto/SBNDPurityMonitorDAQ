from .prm_control_base import *

class MockPrMControl(PrMControlBase):
    '''
    Controls the PrM via an arduino.
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        super(MockPrMControl, self).__init__(prm_ids=prm_ids, config=config)

        self._logger.info('MockPrMControl created.')


    def start_prm(self, prm_id=1):
        '''
        Starts the PrM.
        '''
        self._logger.info('MockPrMControl start_prm.')
        return


    def stop_prm(self, prm_id=1):
        '''
        Stops the PrM.
        '''
        self._logger.info('MockPrMControl stop_prm.')
        return
