import numpy as np
import time, datetime
import logging

from PyQt5.QtCore import QThreadPool, QTimer

from sbndprmdaq.digitizer.mock_ats310 import MockATS310
from sbndprmdaq.parallel_communication.mock_communicator import MockCommunicator
from sbndprmdaq.threading_utils import Worker

class MockPrMManager():

    def __init__(self, window=None):
        self._logger = logging.getLogger(__name__)
        self._ats310 = MockATS310()
        self._comm = MockCommunicator()
        self._window = window

        self._data = [None, None, None]

        self._threadpool = QThreadPool()
        self._logger.info(f'Number of available threads: {self._threadpool.maxThreadCount()}')

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
        # Tell the parallel communicator to start the purity monitor
        self._comm.start_prm()

        if self._window is not None:
            # Start a thread where we let the digitizer run
            self.start_io_thread(prm_id)
        else:
            self.capture_data(prm_id)


    def stop_prm(self, prm_id):
        '''
        Sets the parallel port pin that turns the PrM OFF
        '''
        self._comm.stop_prm()



    def start_io_thread(self, prm_id):
        '''
        Starts the thread.
        '''
        worker = Worker(self.capture_data, prm_id=prm_id)
        worker.signals.result.connect(self._result_callback)
        worker.signals.finished.connect(self._thread_complete)
        worker.signals.progress.connect(self._thread_progress)

        self._threadpool.start(worker)
        self._logger.info(f'Thread started for prm_id {prm_id}.')


    def capture_data(self, prm_id, progress_callback=None):
        '''
        This is the main function that runs in the thread.
        '''

        #
        # Wait some time for the HV to stabilize
        #
        purity_mon_wake_time = 4 #seconds
        start = time.time()
        while(purity_mon_wake_time > time.time() - start):
            perc = (time.time() - start) / purity_mon_wake_time * 100
            if progress_callback is not None:
                progress_callback.emit(prm_id, 'Awake Monitor', perc)
            time.sleep(0.1)

        if progress_callback is not None:
            progress_callback.emit(prm_id, 'Start Capture', 100)

        #
        # Tell the digitizer to start capturing data and check until it completes
        #
        self._ats310.start_capture()
        status = self._ats310.check_capture(prm_id, progress_callback)

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
        This method is called at the end of every thread and receives the acquired data
        '''
        # print('Got data:', parameter, data)
        print('Got data:', data['prm_id'])

        self._data[data['prm_id']-1] = {
            'A': data['A'],
            'B': data['B'],
            'time': data['time'],
        }


    def _thread_progress(self, prm_id, name, s):
        '''
        Called during the thread.
        '''
        self._window.set_progress(prm_id=prm_id, name=name, perc=s)


    def _thread_complete(self, prm_id, status):
        '''
        Called when a thread ends.
        '''
        self._logger.info(f'Thread completed for prm_id {prm_id}.')
        self._comm.stop_prm()
        self._window.start_stop_prm(prm_id)

        if status:
            self._window.reset_progress(prm_id, name='Done!', color='#006400') # #006400 is dark green
        else:
            self._window.reset_progress(prm_id, name='Failed!', color='#B22222') # #B22222 is firebrick

        QTimer.singleShot(3000, lambda: self._window.reset_progress(prm_id))


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
