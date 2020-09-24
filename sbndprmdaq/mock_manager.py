# from sbndprmdaq.digitizer import ATS310
from sbndprmdaq.parallel_communication.mock_communicator import MockCommunicator


class MockPrMManager():

    def __init__(self):
        print('Hello!')
        self._comm = MockCommunicator()


    def test(self):

        print('ok, tested')


     def start_prm(self):
        '''
        Sets the parallel port pin that turns the PrM ON
        '''
        self._comm.start_prm()


    def stop_prm(self):
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
