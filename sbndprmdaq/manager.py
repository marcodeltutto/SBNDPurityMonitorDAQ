from sbndprmdaq.digitizer import ATS310
from sbndprmdaq.parallel_communication.communicator import Communicator

class PrMManager():

    def __init__(self):
        self._ats310 = ATS310()
        self._comm = Communicator()


    def test(self):

        self._ats310.set_records_per_capture(1)
        self._ats310.acquire_data()

        while not self._ats310.busy():
            time.sleep(10e-3)

        data = self._ats310.get_data()
        print(data)


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
