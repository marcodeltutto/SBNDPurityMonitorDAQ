import parallel as pyp
import logging

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
        super(PrMControlException, self).__init__(self._message)


class PrMControlBase():
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
                f'Need to set prm_ids.')

        self._logger.info('PrMControlBase created.')


    def start_prm(self, prm_id=None):
        '''
        Turns the PrM ON.
        '''
        print('To be implemented')
        return


    def stop_prm(self, prm_id=None):
        '''
        Turns the PrM OFF.
        '''
        print('To be implemented')
        return

