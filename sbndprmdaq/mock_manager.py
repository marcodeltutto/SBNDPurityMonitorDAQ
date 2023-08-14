'''
The purity monitor mock manager (for testing).
'''
import os
import time
import datetime
import logging
import numpy as np

from PyQt5.QtCore import QThreadPool, QTimer

from sbndprmdaq.digitizer.mock_ats310 import MockATS310, get_digitizers
from sbndprmdaq.communication.mock_communicator import MockCommunicator
from sbndprmdaq.threading_utils import Worker

from sbndprmdaq.digitizer.mock_prm_digitizer import MockPrMDigitizer

class MockPrMManager():
    '''
    A mock purity monitor manager. Takes care of all DAQ aspects.
    '''

    def __init__(self, config, window=None):
        '''
        Constructor. Can be called passing the GUI main window if the GUI is desired.

        Args:
            window (QMainWindow): The main window (optional).
        '''
        self._logger = logging.getLogger(__name__)

        self._comm = MockCommunicator()
        # self._prm_control = MockPrMControl(prm_ids=[1,2,3], config=config)
        # self._hv_control = MockHVControl(prm_ids=[1,2,3], config=config)
        self._prm_digitizer = MockPrMDigitizer(config)

        self._window = window

        self._digitizers = {}
        self._data = {}
        self._is_running = {}
        self._run_numbers = {}

        digitizers = get_digitizers(config['prm_id_to_ats_systemid'])
        for prm_id, digitizer in digitizers.items():
            if digitizer is None:
                if self._window is not None:
                    self._window.missing_digitizer(prm_id)
                continue
            self._digitizers[prm_id] = digitizer
            self._data[prm_id] = None
            self._is_running[prm_id] = False
            self._run_numbers[prm_id] = None

        self._threadpool = QThreadPool()
        self._logger.info('Number of available threads: {n_thread}'.format(
                          n_thread=self._threadpool.maxThreadCount()))

        self._data_files_path = config['data_files_path']
        self.retrieve_run_numbers()

    def exit(self):

        self._logger.info('Exiting.')

    def heartbeat(self):

        return

    def digitizer_busy(self, prm_id):
        '''
        Returns the digitizers status
        (if it is busy or now)

        Args:
            prm_id (int): The purity monitor ID.
        Returns:
            bool: True for busy, False otherwise.
        '''
        return self._digitizers[prm_id].busy()


    def ats_samples_per_sec(self, prm_id=1):
        '''
        Returns the digitizer recorded samples per second

        Args:
            prm_id (int): The purity monitor ID.
        Returns:
            bool: The digitizer samples per second
        '''
        return self._digitizers[prm_id].get_samples_per_second()


    def start_prm(self, prm_id):
        '''
        Sets the parallel port pin that turns the PrM ON
        and starts the thread for the data acquisition.
        If no GUI is present, the thread is not started.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        # Tell the parallel communicator to start the purity monitor
        # self._comm.start_prm()
        # self._prm_control.start_prm()

        if self._window is not None:
            # Start a thread where we let the digitizer run
            self.start_io_thread(prm_id)
        else:
            self.capture_data(prm_id)


    def stop_prm(self, prm_id):
        '''
        Sets the parallel port pin that turns the PrM OFF.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._comm.stop_prm()
        # self._prm_control.stop_prm()



    def start_io_thread(self, prm_id):
        '''
        Starts the thread.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        worker = Worker(self.capture_data, prm_id=prm_id)
        worker.signals.result.connect(self._result_callback)
        worker.signals.finished.connect(self._thread_complete)
        worker.signals.progress.connect(self._thread_progress)

        self._threadpool.start(worker)
        self._logger.info('Thread started for prm_id {prm_id}.'.format(prm_id=prm_id))


    def capture_data(self, prm_id, progress_callback=None):
        '''
        Capture the data. If running without a GUI, do not pass the progress_callback.

        Args:
            prm_id (int): The purity monitor ID.
            progress_callback (fn): The callback function to be called to show progress (optional)
        Returns:
            dict: A dictionary containing the prm_id, the status,
            the data for ch A, the data for ch B
        '''

        #
        # Wait some time for the HV to stabilize
        #
        purity_mon_wake_time = 4 #seconds
        start = time.time()
        while purity_mon_wake_time > time.time() - start:
            perc = (time.time() - start) / purity_mon_wake_time * 100
            if progress_callback is not None:
                progress_callback.emit(prm_id, 'Awake Monitor', perc)
            time.sleep(0.1)

        if progress_callback is not None:
            progress_callback.emit(prm_id, 'Start Capture', 100)

        #
        # Tell the digitizer to start capturing data and check until it completes
        #
        self._digitizers[prm_id].start_capture()
        status = self._digitizers[prm_id].check_capture(prm_id, progress_callback)

        # Generate random data
        records_per_capture = 3
        sample_size = 8
        data = {
            'prm_id': prm_id,
            'status': status,
            'time': datetime.datetime.today(),
            'A': [np.random.normal(loc=0.0, scale=1.0, size=sample_size)] * records_per_capture,
            'B': [np.random.normal(loc=0.0, scale=1.0, size=sample_size)] * records_per_capture
        }

        return data


    def _result_callback(self, data):
        '''
        This method is called at the end of every thread and receives the acquired data.

        Args:
            data (dict): The acquired data.
        '''
        # print('Got data:', parameter, data)
        print('Got data:', data['prm_id'])

        self._data[data['prm_id']-1] = {
            'A': data['A'],
            'B': data['B'],
            'time': data['time'],
        }


    def _thread_progress(self, prm_id, name, progress):
        '''
        Callback called during a thread to show progress.

        Args:
            prm_id (int): The purity monitor ID.
            name (str): The name of the current task for display.
            progress (int): The progress (0 to 100 percent).
        '''
        self._window.set_progress(prm_id=prm_id, name=name, perc=progress)


    def _thread_complete(self, prm_id, status):
        '''
        Called when a thread ends.

        Args:
            prm_id (int): The purity monitor ID.
            status (bool): True is the acquisition suceeded, False otherwise.
        '''
        self._logger.info('Thread completed for prm_id {prm_id}.'.format(prm_id=prm_id))
        self._comm.stop_prm()
        self._window.start_stop_prm(prm_id)

        if status:
            self._window.reset_progress(prm_id, name='Done!', color='#006400') # dark green
        else:
            self._window.reset_progress(prm_id, name='Failed!', color='#B22222') # firebrick

        QTimer.singleShot(3000, lambda: self._window.reset_progress(prm_id))


    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._comm.hv_on()


    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._comm.hv_off()

    def set_mode(self, prm_id, mode):
        '''
        Sets the mode (auto, manual).

        Args:
            prm_id (int): The purity monitor ID.
            mode (int): The desired mode.
        '''
        print('Mode for', prm_id, 'set to', mode)

    def get_data(self, prm_id):
        '''
        Sets the mode (auto, manual).

        Args:
            prm_id (int): The purity monitor ID.

        Returns:
            dict: A dictionary containing the data for ch A and for ch B.
        '''
        return self._data[prm_id]

    def get_hv(self, prm_id):
        '''
        Returns the HV values for the cathode and anode

        Args:
            prm_id (int): The purity monitor ID.

        Returns:
            float: The cathode HV.
            float: The anode HV.
        '''
        cathode_hv = self._hv_control.get_hv_sense_value('cathode', prm_id)
        anode_hv = self._hv_control.get_hv_sense_value('anode', prm_id)
        anodegrid_hv = self._hv_control.get_hv_sense_value('anodegrid', prm_id)

        return cathode_hv, anode_hv, anodegrid_hv

    def get_hv_status(self, prm_id):
        '''
        Returns whether the HV is on or off for the cathode and anode

        Args:
            prm_id (int): The purity monitor ID.

        Returns:
            bool: Whether the cathode HV is on or not.
            bool: Whether the anode HV is on or not.
        '''
        if prm_id == 1:
            return True, True, True
        else:
            return True, False, False



    def set_comment(self, comment):
        self._comment = comment

    def is_running(self, prm_id):
        return False

    def get_n_acquisitions(self, prm_id):
        return 1

    def retrieve_run_numbers(self):
        if self._data_files_path is None:
            self._logger.warning('Cannot retrieve run number as data_files_path is not set.')
            return

        if not os.path.exists(self._data_files_path):
            self._logger.error('data_files_path is not a real path.')
            return

        run_file_name = self._data_files_path + '/latest_run_number.txt'

        if not os.path.exists(run_file_name):
            self._logger.info('Latest run file doesnt exist.')
            f = open(run_file_name, "w")
            for k, v in self._run_numbers.items():
                self._run_numbers[k] = -1
                f.write(str(k) + ' ' + str(self._run_numbers[k]) + '\n')
        else:
            with open(run_file_name) as f:
                for line in f:
                    prm_id = line.split()[0]
                    run_no = line.split()[1]
                    print('PrM:', prm_id, 'Run No:', run_no)

    def get_run_number(self, prm_id):
        print('run no', self._run_numbers[prm_id])
        return self._run_numbers[prm_id]


