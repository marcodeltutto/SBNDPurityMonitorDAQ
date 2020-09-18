import parallel as pyp

class Communicator():

    def __init__(self, port='/dev/parport0'):

        self._port = pyp.Parallel(port)
        self._port.setData(0)

    def _set_data(self, data):
        '''
        Sets the data to the parallel port
        Examples:
            _set_data(0)    # sets all pins low
            _set_data(255)  # sets all pins high
            _set_data(2)    # sets just pin 3 high (remember that pin2=bit0)
            _set_data(3)    # sets just pins 2 and 3 high
        You can also convert base 2 to int easily in python::
            _set_data(int("00000011", 2))  # pins 2 and 3 high
            _set_data(int("00000101", 2))  # pins 2 and 4 high
        '''
        self._port.setData(data)


    def _read_data(self):
        '''
        Returns the value currently set on the data pins (2-9)
        '''
        return self._port.PPRDATA()


    def _set_pin(self, pin_number, state):
        '''
        Set a desired pin to be high(1) or low(0).
        Only pins 2-9 (incl) are normally used for data output::
            _set_pin(3, 1)  # sets pin 3 high
            _set_pin(3, 0)  # sets pin 3 low
        '''
        if state:
            self._port.setData(self._port.PPRDATA() | (2**(pin_number - 2)))
        else:
            self._port.setData(self._port.PPRDATA() & (255 ^ 2**(pin_number - 2)))

    def _read_pin(self, pin_number):
        '''
        Determines whether a desired (input) pin is high(1) or low(0).
        Pins 2-13 and 15 are currently read here
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
            print(f'Pin {pin_number} cannot be read.')


    def start_prm(self):
        '''
        Sets the parallel port pin that turns the PrM ON
        '''
        self._set_pin(2, 1)


    def stop_prm(self):
        '''
        Sets the parallel port pin that turns the PrM OFF
        '''
        self._set_pin(2, 0)


    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON
        '''
        self._set_pin(5, 1)


    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        self._set_pin(5, 0)