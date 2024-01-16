'''
Contains base abstract class for the digitizer
'''

from abc import ABC, abstractmethod

class DigitizerBase(ABC):
    '''
    A base abstract class for the digitizer
    '''

    def __init__(self):
        pass

    @abstractmethod
    def busy(self):
        '''Returns true is the digitizer is busy'''

    @abstractmethod
    def get_trigger_sample(self):
        '''Returns the number of samples when the trigger happens'''

    @abstractmethod
    def get_samples_per_second(self):
        '''Returns the number of samples acquired per second'''

    @abstractmethod
    def set_samples_per_second(self, samples):
        '''Sets he number of samples acquired per second'''

    @abstractmethod
    def get_number_acquisitions(self):
        '''Returnes the number of triggers acquired'''

    @abstractmethod
    def set_number_acquisitions(self, n_acquisitions):
        '''Sets the number of triggers acquired'''

    @abstractmethod
    def get_pre_trigger_samples(self):
        '''Returns the number of samples before the trigges'''

    @abstractmethod
    def get_post_trigger_samples(self):
        '''Returns the number of samples after the trigges'''

    @abstractmethod
    def get_input_range_volts(self):
        '''Returns the range in Volts'''

    @abstractmethod
    def lamp_on(self):
        '''Turns on the flash lamp'''

    @abstractmethod
    def lamp_off(self):
        '''Turns off the flash lamp'''

    @abstractmethod
    def lamp_frequency(self, freq):
        '''Sets the flash lamp frequency'''

    @abstractmethod
    def start_capture(self):
        '''Starts the data capture'''

    @abstractmethod
    def check_capture(self):
        '''Returns true if data has been captured'''

    @abstractmethod
    def get_data(self):
        '''Returns the captured data'''
