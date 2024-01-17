'''
Contains a mock PrM digitizer class for testing purposed
'''

import datetime
import numpy as np
from .prm_digitizer import PrMDigitizer, DigitizerBase


class MockDigitizer(DigitizerBase):
    '''
    A mock PrM digitizer class for testing purposed
    '''

    def busy(self):
        '''Returns true is the digitizer is busy'''
        return 1

    def get_trigger_sample(self):
        '''Returns the number of samples when the trigger happens'''
        return 1

    def get_samples_per_second(self):
        '''Returns the number of samples acquired per second'''
        return 1

    def set_samples_per_second(self, samples):
        '''Sets he number of samples acquired per second'''
        print('set_samples_per_second to', samples)

    def get_number_acquisitions(self):
        '''Returnes the number of triggers acquired'''
        return 1

    def set_number_acquisitions(self, n_acquisitions):
        '''Sets the number of triggers acquired'''
        print('set_number_acquisitions to', n_acquisitions)

    def get_pre_trigger_samples(self):
        '''Returns the number of samples before the trigges'''
        return 1

    def get_post_trigger_samples(self):
        '''Returns the number of samples after the trigges'''
        return 1

    def get_input_range_volts(self):
        '''Returns the range in Volts'''
        return 1

    def lamp_on(self):
        '''Turns on the flash lamp'''
        return 1

    def lamp_off(self):
        '''Turns off the flash lamp'''
        return 1

    def lamp_frequency(self, freq):
        '''Sets the flash lamp frequency'''
        return 1

    def start_capture(self):
        '''Starts the data capture'''
        return 1

    def check_capture(self):
        '''Returns true if data has been captured'''
        return 1

    def get_data(self):
        '''Returns the captured data'''
        records_per_capture=1
        sample_size=4096
        data = {
            'prm_id': 1,
            'status': True,
            'time': datetime.datetime.today(),
            'A': [np.random.normal(loc=0.0, scale=1.0, size=sample_size)] * records_per_capture,
            'B': [np.random.normal(loc=0.0, scale=1.0, size=sample_size)] * records_per_capture
        }
        return data


class MockPrMDigitizer(PrMDigitizer):
    '''
    A MockPrMDigitizer class for testing purposes
    '''

    def _get_adpro_digitizer(self, prm_id, config):
        '''
        Overrides
        '''
        return MockDigitizer()

    def _get_ats310_digitizer(self, systemid, config=None):
        '''
        Overrides
        '''
        return MockDigitizer()
