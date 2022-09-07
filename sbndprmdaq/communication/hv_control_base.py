import logging

class HVControlException(Exception):
    '''
    Exception class for ATS310.
    '''

    def __init__(self, logger, message):
        '''
        Contructor.

        Args:
            logger (PrMLogger): The logger widget.
            message (str): The error message.
        '''
        self._message = message
        logger.critical(self._message)
        super(HVControlException, self).__init__(self._message)


class HVControlBase():
    '''
    A base class to control the HV.
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''

        self._logger = logging.getLogger(__name__)

        if prm_ids is None:
            raise HVControlException(self._logger,
                f'Need to set prm_ids.')

        self._logger.info('HVControl created.')

    def is_crate_on(self):
        '''
        Returns True if the crate is ON
        '''
        print('To be implemented')
        return


    def hv_on(self, prm_id=1):
        '''
        Turn the HV ON.
        '''
        print('To be implemented')
        return


    def hv_off(self, prm_id=1):
        '''
        Turn the HV OFF.
        '''
        print('To be implemented')
        return

