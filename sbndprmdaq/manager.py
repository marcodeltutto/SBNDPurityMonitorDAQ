import time, copy
import logging
import numpy as np

from sbndprmdaq.digitizer.ats310 import get_digitizers, ATS310Exception #, ATS310,
from sbndprmdaq.digitizer.board_wrapper import BoardWrapper
from sbndprmdaq.parallel_communication.communicator import Communicator

class PrMManager():

    def __init__(self, data_files_path):
        self._logger = logging.getLogger(__name__)
        # self._ats310 = ATS310()
        # self._ats310 = BoardWrapper(self._ats310, self._logger, ATS310Exception)
        self._comm = Communicator()

        digitizers = get_digitizers()
        self._digitizers = []
        self._data = []
        for d in digitizers:
            self._digitizers.append(BoardWrapper(d, self._logger, ATS310Exception))
            self._data.append(None)
        self._data_files_path = data_files_path

        self._hv_on = False


    # def test(self):

    #     self._ats310.set_records_per_capture(1)
    #     self._ats310.acquire_data()

    #     while not self._ats310.busy():
    #         time.sleep(10e-3)

    #     data = self._ats310.get_data()
    #     print(data)

    def digitizer_busy(self, prm_id=1):
        '''
        Returns the digitizers status
        (if it is busy or now)
        '''
        self._ats310 = self._digitizers[prm_id-1]
        return self._ats310.busy()

    def ats_samples_per_sec(self):
        return self._ats310.get_samples_per_second()

    def start_prm(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the PrM ON
        '''
        self._ats310 = self._digitizers[prm_id-1]
        self._ats310.start_capture()
        self._comm.start_prm()
        time.sleep(8)
        self._ats310.start_capture()
        self._ats310.check_capture()

        self._data[prm_id-1] = self._ats310.get_data()
        print('From manager:', self._data[prm_id-1])

        self._save_data(prm_id)

    def _save_data(self, prm_id=1):
        '''
        Saves data to file
        '''

        out_dict = {}

        timestr = time.strftime("%Y%m%d-%H%M%S")

        for ch in self._data[prm_id-1].keys():
            # file_name = self._data_files_path + '/sbnd_prm_data_' + timestr + '_' + ch + '.csv'
            # np.savetxt(file_name, self._data[ch], delimiter=',')
            # self._logger.info(f'Saving data for ch {ch} to file ' + file_name)

            out_dict[f'ch_{ch}'] = self._data[ch]

        if self._hv_on:
            hv_status = 'on'
        else:
            hv_status = 'off'

        file_name = self._data_files_path + '/sbnd_prm_data_' + timestr + '_hv_' + hv_status
        np.savez(file_name, **out_dict)

    def stop_prm(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the PrM OFF
        '''
        self._comm.stop_prm()


    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON
        '''
        self._comm.hv_on()
        self._hv_on = True


    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        self._comm.hv_off()
        self._hv_on = False

    def set_mode(self, prm_id, mode):
        return

    def get_data(self, prm_id):
        '''
        '''
        return self._data[prm_id-1]
