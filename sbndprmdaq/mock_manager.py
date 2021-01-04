from sbndprmdaq.digitizer.mock_ats310 import MockATS310
from sbndprmdaq.parallel_communication.mock_communicator import MockCommunicator
import numpy as np

class MockPrMManager():

    def __init__(self):
        print('Hello!')
        self._ats310 = MockATS310()
        self._comm = MockCommunicator()

        self._data = [None, None, None]


    def test(self):

        print('ok, tested')

    def digitizer_busy(self, prm_id):
        '''
        Returns the digitizers status
        (if it is busy or now)
        '''
        return self._ats310.busy()

    def ats_samples_per_sec(self):
        return self._ats310.get_samples_per_second()


    def start_prm(self, prm_id):
        '''
        Sets the parallel port pin that turns the PrM ON
        '''
        self._ats310.start_capture()

        # Generate random data
        records_per_capture = 10
        self._data[prm_id - 1] = {
            'A': [np.random.normal(loc=0.0, scale=1.0, size=512)] * records_per_capture,
            'B': [np.random.normal(loc=0.0, scale=1.0, size=512)] * records_per_capture
        }
        self._comm.start_prm()


    def stop_prm(self, prm_id):
        '''
        Sets the parallel port pin that turns the PrM OFF
        '''
        self._comm.stop_prm()


    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON
        '''
        self._comm.hv_on()


    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        self._comm.hv_off()

    def set_mode(self, prm_id, mode):
        print('Mode for', prm_id, 'set to', mode)
        return

    def get_data(self, prm_id):
        '''
        '''
        return self._data[prm_id-1]
