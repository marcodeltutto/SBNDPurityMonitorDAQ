import parallel as pyp
import logging

class ParallelException(Exception):
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
        super(ParallelException, self).__init__(self._message)


class Communicator():
    '''
    The communicator class that deals with the parallel port.
    '''

    def __init__(self, port='/dev/parport0', prm_id=1):
        '''
        Contructor.

        Args:
            port (str): The path to the parallel port.
            prm_id (int): The purity monitor ID.
        '''

        self._logger = logging.getLogger(__name__)

        self._port = pyp.Parallel(port)
        self._port.setData(0)
        self._prm_id = prm_id

        if not self._check_data(data_sent=0):
            raise ParallelException(self._logger,
                f'Cannot set data to parallel port in constructor. Tried to send: {data}.')

        self._logger.info('Parallel communicator created.')

    def _set_data(self, data):
        '''
        Sets the data to the parallel port.
        Examples:
            _set_data(0)    # sets all pins low
            _set_data(255)  # sets all pins high
            _set_data(2)    # sets just pin 3 high (remember that pin2=bit0)
            _set_data(3)    # sets just pins 2 and 3 high
        You can also convert base 2 to int easily in python::
            _set_data(int("00000011", 2))  # pins 2 and 3 high
            _set_data(int("00000101", 2))  # pins 2 and 4 high

        Args:
            data(int): The data to be set.
        '''
        self._port.setData(data)

        if not self._check_data(data_sent=data):
            raise ParallelException(self._logger,
                f'Cannot set data to parallel port. Tried to send: {data}.')


    def _read_data(self):
        '''
        Returns the value currently set on the data pins (2-9)

        Returns:
            int: value currently set on the data pins (2-9)
        '''
        return self._port.PPRDATA()


    def _check_data(self, data_sent=None):
        '''
        Checks if the data sent is correct.

        Args:
            data_sent (int): The sent data to be checked.
        '''
        if data_sent is None:
            raise ParallelException(self._logger,
                'Wrong use of _check_data method. Cannot pass None.')

        return data_sent == self._read_data()



    def _set_pin(self, pin_number, state):
        '''
        Set a desired pin to be high (1) or low (0).
        Only pins 2-9 (incl) are normally used for data output::
            _set_pin(3, 1)  # sets pin 3 high
            _set_pin(3, 0)  # sets pin 3 low

        Args:
            pin_number (int): The pin number.
            state(int): The state to set: 1 or 0.
        '''
        if state:
            self._set_data(self._port.PPRDATA() | (2**(pin_number - 2)))
        else:
            self._set_data(self._port.PPRDATA() & (255 ^ 2**(pin_number - 2)))

    def _read_pin(self, pin_number):
        '''
        Determines whether a desired (input) pin is high(1) or low(0).
        Pins 2-13 and 15 are currently read here

        Args:
            pin_number (int): The pin number.
        '''
        if pin_number == 10:
            return self._port.getInAcknowledge()
        elif pin_number == 11:
            return self._port.getInBusy()
        elif pin_number == 12:
            return self._port.getInPaperOut()
        elif pin_number == 13:
            return self._port.getInSelected()
        elif pin_number == 15:
            return self._port.getInError()
        elif 2 <= pin_number <= 9:
            return (self._port.PPRDATA() >> (pin_number - 2)) & 1
        else:
            self._logger.error(f'Pin {pin_number} cannot be read.')


    def start_prm(self):
        '''
        Sets the parallel port pin that turns the PrM ON.
        '''
        self._logger.info(f'Starting purity monitor {self._prm_id}.')
        self._set_pin(2, 1)


    def stop_prm(self):
        '''
        Sets the parallel port pin that turns the PrM OFF.
        '''
        self._logger.info(f'Stopping purity monitor {self._prm_id}.')
        self._set_pin(2, 0)


    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON.
        '''
        self._logger.info(f'HV set to ON for PrM ID {self._prm_id}.')
        self._set_pin(6, 1)


    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        self._logger.info(f'HV set to OFF for PrM ID {self._prm_id}.')
        self._set_pin(6, 0)
