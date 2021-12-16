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

    def __init__(self, prm_id=1, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
            config (dict): Settings
        '''

        self._logger = logging.getLogger(__name__)

        self._prm_id = prm_id
        self._setting = config

            # raise PrMControlException(self._logger,
            #     f'Cannot set data to parallel port in constructor. Tried to send: {data}.')

        self._logger.info('PrMControlBase created.')


    def start_prm(self):
        '''
        Turns the PrM ON.
        '''
        print('To be implemented')
        return


    def stop_prm(self):
        '''
        Turns the PrM OFF.
        '''
        print('To be implemented')
        return

