'''
The purity monitor manager.
'''
import time
import logging
import numpy as np

from PyQt5.QtCore import QThreadPool, QTimer

from sbndprmdaq.digitizer.ats310 import get_digitizers, ATS310Exception #, ATS310,
from sbndprmdaq.digitizer.board_wrapper import BoardWrapper
from sbndprmdaq.parallel_communication.communicator import Communicator
from sbndprmdaq.threading_utils import Worker

class PrMManager():
    '''
    The purity monitor manager. Takes care of all DAQ aspects.
    '''
    # pylint: disable=too-many-instance-attributes

    def __init__(self, config, window=None):
        '''
        Constructor. Can be called passing the GUI main window if the GUI is desired.

        Args:
            window (QMainWindow): The main window (optional).
            data_files_path (str): The path where files will be saved (optional).
        '''
        self._logger = logging.getLogger(__name__)
        # self._ats310 = ATS310()
        # self._ats310 = BoardWrapper(self._ats310, self._logger, ATS310Exception)
        self._window = window
        self._comm = Communicator()

        self._digitizers = {}
        self._data = {}

        digitizers = get_digitizers(config['prm_id_to_ats_systemid'])
        for prm_id, digitizer in digitizers.items():
            if digitizer is None:
                self._window.missing_digitizer(prm_id)
                continue
            self._digitizers[prm_id] = BoardWrapper(digitizer, self._logger, ATS310Exception)
            self._data[prm_id] = None

        self._logger.info('Number of available digitizers: {n_digi}'.format(
                          n_digi=len(self._digitizers)))

        self._data_files_path = prm_id_to_ats_systemid['data_files_path']

        self._hv_on = False

        self._threadpool = QThreadPool()
        self._logger.info('Number of available threads: {n_thread}'.format(
                          n_thread=self._threadpool.maxThreadCount()))


    def digitizer_busy(self, prm_id=1):
        '''
        Returns the digitizers status
        (if it is busy or now)

        Args:
            prm_id (int): The purity monitor ID.
        Returns:
            bool: True for busy, False otherwise.
        '''
        ats310 = self._digitizers[prm_id]
        return ats310.busy()


    def ats_samples_per_sec(self, prm_id=1):
        '''
        Returns the digitizer recorded samples per second

        Returns:
            bool: The digitizer samples per second
        '''
        ats310 = self._digitizers[prm_id]
        return ats310.get_samples_per_second()


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

        ats310 = self._digitizers[prm_id]

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
        ats310.start_capture()
        status = ats310.check_capture(prm_id, progress_callback)

        data_raw = ats310.get_data()
        # print('From manager:', data)
        data = {
            'prm_id': prm_id,
            'status': status,
            'A': data_raw['A'],
            'B': data_raw['B'],
        }

        return data


    def _result_callback(self, data):
        '''
        This method is called at the end of every thread and receives the acquired data.

        Args:
            data (dict): The acquired data.
        '''
        print('Got data:', data['prm_id'])

        if data['status']:
            print('ok')
            self._data[data['prm_id']] = {
                'A': data['A'],
                'B': data['B'],
            }
            self.save_data(data['prm_id'])


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
        self._window.start_stop_prm(prm_id)

        if status:
            self._window.reset_progress(prm_id, name='Done!', color='#006400') # dark green
        else:
            self._window.reset_progress(prm_id, name='Failed!', color='#B22222') # firebrick

        QTimer.singleShot(3000, lambda: self._window.reset_progress(prm_id))


    def save_data(self, prm_id=1):
        '''
        Saves the most recent captured data, if any.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        # pylint: disable=invalid-name

        out_dict = {}

        timestr = time.strftime("%Y%m%d-%H%M%S")

        if self._data[prm_id] is None:
            return

        for ch in self._data[prm_id].keys():
            # file_name = self._data_files_path + '/sbnd_prm_data_' + timestr + '_' + ch + '.csv'
            # np.savetxt(file_name, self._data[ch], delimiter=',')
            # self._logger.info(f'Saving data for ch {ch} to file ' + file_name)

            out_dict[f'ch_{ch}'] = self._data[prm_id][ch]

        if self._hv_on:
            hv_status = 'on'
        else:
            hv_status = 'off'

        file_name = self._data_files_path
        file_name += '/sbnd_prm'
        file_name += str(prm_id)
        file_name += '_data_'
        file_name += timestr
        file_name += '_hv_'
        file_name += hv_status

        np.savez(file_name, **out_dict)


    def start_prm(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the PrM ON
        and starts the thread for the data acquisition.
        If no GUI is present, the thread is not started.

        Args:
            prm_id (int): The purity monitor ID.
        '''

        # Tell the parallel communicator to start the purity monitor
        self._comm.start_prm()

        if self._window is not None:
            # Start a thread where we let the digitizer run
            self.start_io_thread(prm_id)
        else:
            self.capture_data(prm_id)


    def stop_prm(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the PrM OFF.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._comm.stop_prm()


    def hv_on(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the HV ON.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._comm.hv_on()
        self._hv_on = True


    def hv_off(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the HV OFF.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._comm.hv_off()
        self._hv_on = False


    def set_mode(self, prm_id, mode):
        '''
        Sets the mode (auto, manual).

        Args:
            prm_id (int): The purity monitor ID.
            mode (int): The desired mode.
        '''
        return


    def get_data(self, prm_id):
        '''
        Sets the mode (auto, manual).

        Args:
            prm_id (int): The purity monitor ID.

        Returns:
            dict: A dictionary containing the data for ch A and for ch B.
        '''
        return self._data[prm_id]
