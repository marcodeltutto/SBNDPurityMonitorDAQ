'''
Contains Base abstract class for PrM control module
'''
import logging
from abc import ABC, abstractmethod

class PrMControlException(Exception):
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


class PrMControlBase(ABC):
    '''
    The communicator class that deals with the parallel port.
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_ids (list): The purity monitor IDs.
            config (dict): Settings
        '''

        self._logger = logging.getLogger(__name__)

        if prm_ids is None:
            raise PrMControlException(self._logger,
                'Need to set prm_ids.')

        if config is None:
            raise PrMControlException(self._logger,
                'Need to set config.')

        self._logger.info('PrMControlBase created.')


    @abstractmethod
    def start_prm(self, prm_id=None):
        '''
        Turns the PrM ON.
        '''
        pass


    @abstractmethod
    def stop_prm(self, prm_id=None):
        '''
        Turns the PrM OFF.
        '''
        pass
