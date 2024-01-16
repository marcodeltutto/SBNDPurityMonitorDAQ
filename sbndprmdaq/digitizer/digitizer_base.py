from abc import ABC, abstractmethod 

class DigitizerBase(ABC):

    def __init__(self):
        pass


    @abstractmethod
    def busy(self):
        '''Returns true is the digitizer is busy'''
        pass

    @abstractmethod
    def get_trigger_sample(self):
        '''Returns the number of samples when the trigger happens'''
        pass

    @abstractmethod
    def get_samples_per_second(self):
        '''Returns the number of samples acquired per second'''
        pass

    @abstractmethod
    def set_samples_per_second(self, n):
        '''Sets he number of samples acquired per second'''
        pass

    @abstractmethod
    def get_number_acquisitions(self):
        '''Returnes the number of triggers acquired'''
        pass

    @abstractmethod
    def set_number_acquisitions(self, n):
        '''Sets the number of triggers acquired'''
        pass

    @abstractmethod
    def get_pre_trigger_samples(self):
        '''Returns the number of samples before the trigges'''
        pass

    @abstractmethod
    def get_post_trigger_samples(self):
        '''Returns the number of samples after the trigges'''
        pass

    @abstractmethod
    def get_input_range_volts(self):
        '''Returns the range in Volts'''
        pass

    @abstractmethod
    def lamp_on(self):
        '''Turns on the flash lamp'''
        pass

    @abstractmethod
    def lamp_off(self):
        '''Turns off the flash lamp'''
        pass

    @abstractmethod
    def lamp_frequency(self, freq):
        '''Sets the flash lamp frequency'''
        pass

    @abstractmethod
    def start_capture(self):
        '''Starts the data capture'''
        pass

    @abstractmethod
    def check_capture(self):
        '''Returns true if data has been captured'''
        pass

    @abstractmethod
    def get_data(self):
        '''Returns the captured data'''
        pass




