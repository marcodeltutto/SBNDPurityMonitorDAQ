import logging
import serial

class SerialException(Exception):
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
        super(SerialException, self).__init__(self._message)


class Communicator():
    '''
    The serial communicator class that deals with the serial port.
    '''

    def __init__(self, port='/dev/ttyS0', prm_id=1):
        '''
        Contructor.

        Args:
            port (str): The path to the parallel port.
            prm_id (int): The purity monitor ID.
        '''

        self._logger = logging.getLogger(__name__)

        self._ser = serial.Serial()
        self._ser.port = port
        self._ser.dtr = False
        self._ser.rts = False
        self._ser.open()

        self._prm_id = prm_id

        if not self._ser.is_open:
            raise ParallelException(self._logger,
                f'Cannot set data to parallel port in constructor. Tried to send: {data}.')

        self._logger.info('Parallel communicator created.')

    def __del__(self):
        '''
        Destructor
        '''
        self._ser.close()

    def start_prm(self):
        '''
        Sets the parallel port pin that turns the PrM ON.
        '''
        self._logger.info(f'Starting purity monitor {self._prm_id}.')
        self._ser.rts = True


    def stop_prm(self):
        '''
        Sets the parallel port pin that turns the PrM OFF.
        '''
        self._logger.info(f'Stopping purity monitor {self._prm_id}.')
        self._ser.rts = False


    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON.
        '''
        self._logger.info(f'HV set to ON for PrM ID {self._prm_id}.')
        self._ser.dtr = False


    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        self._logger.info(f'HV set to OFF for PrM ID {self._prm_id}.')
        self._ser.dtr = True
