'''
Contains base class for HV control
'''
import logging
from abc import ABC, abstractmethod

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
        super().__init__(self._message)


#pylint: disable=invalid-name
class HVControlBase(ABC):
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
                'Need to set prm_ids.')

        self._config = config

        self._logger.info('HVControl created.')

    @abstractmethod
    def is_crate_on(self, ip):
        '''
        Returns True if the crate is ON
        '''

    @abstractmethod
    def hv_on(self, prm_id=1):
        '''
        Turn the HV ON.
        '''

    @abstractmethod
    def hv_off(self, prm_id=1):
        '''
        Turn the HV OFF.
        '''
