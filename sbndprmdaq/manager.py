'''
The purity monitor manager.
'''
import os
import time
import datetime
import logging
import numpy as np

from PyQt5.QtCore import QThreadPool, QTimer

from sbndprmdaq.threading_utils import Worker
from sbndprmdaq.digitizer.prm_digitizer import PrMDigitizer
from sbndprmdaq.high_voltage.hv_control_mpod import HVControlMPOD

#pylint: disable=too-many-public-methods
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
        self._window = window

        self._digitizers = {}
        self._data = {}
        self._is_running = {}
        self._run_numbers = {}
        self._repetitions = {}

        self._data_files_path = config['data_files_path']
        self._save_as_npz = config['save_as_npz']
        self._save_as_txt = config['save_as_txt']

        for prm_id in config['prm_ids']:
            self._data[prm_id] = None
            self._is_running[prm_id] = False
            self._run_numbers[prm_id] = None
            self._repetitions[prm_id] = 1

        self._set_digitizer_and_hv(config)

        self._logger.info(f'Number of available digitizers: {self._prm_digitizer.n_digitizers()}')

        self._hv_on = False
        self._use_hv = True

        self._threadpool = QThreadPool()
        self._logger.info(f'Number of available threads: {self._threadpool.maxThreadCount()}')

        # A timer used to periodically run the PrMs
        self._timer = QTimer()
        self._mode = 'manual'

        self._comment = 'No comment'

        self.retrieve_run_numbers()


    def _set_digitizer_and_hv(self, config):
        '''
        Sets the PrMDigitizer and HVControlMPOD
        '''
        self._prm_digitizer = PrMDigitizer(config)
        self._hv_control = HVControlMPOD(config['prm_ids'], config=config)


    def exit(self):
        '''
        Called at exit event
        '''

        self._logger.info('Exiting...')

        # for prm_id in self._digitizers.keys():

        #     # Set HV values to 0
        #     self._hv_control.set_hv_value('anode', 0, prm_id)
        #     self._hv_control.set_hv_value('anodegrid', 0, prm_id)
        #     self._hv_control.set_hv_value('cathode', 0, prm_id)
        #     self._logger.info('HV is set to 0.')

        #     # Turn off HV
        #     self.hv_off(prm_id)
        #     self._logger.info('HV is off.')

        #     # Stop the PrM
        #     self._prm_control.stop_prm(prm_id)
        #     self._logger.info('PrM is off.')

        # Delete digiter log file
        os.remove('/tmp/ATSApi.log')



    def digitizer_busy(self, prm_id=1):
        '''
        Returns the digitizers status
        (if it is busy or not)

        Args:
            prm_id (int): The purity monitor ID.
        Returns:
            bool: True for busy, False otherwise.
        '''
        # ats310 = self._digitizers[prm_id]
        # return ats310.busy()
        return self._prm_digitizer.busy(prm_id)


    def ats_trigger_sample(self, prm_id=1):
        '''
        returns the sample when the trigger happens.

        Returns:
            int: Sample number when triggered.
        '''
        # ats310 = self._digitizers[prm_id]
        # return ats310.get_trigger_sample()
        return self._prm_digitizer.get_trigger_sample(prm_id)

    def ats_samples_per_sec(self, prm_id=1):
        '''
        Returns the digitizer recorded samples per second

        Returns:
            bool: The digitizer samples per second
        '''
        # ats310 = self._digitizers[prm_id]
        # return ats310.get_samples_per_second()
        return self._prm_digitizer.get_samples_per_second(prm_id)

    def get_number_acquisitions(self, prm_id=1):
        '''
        Returns the digitizer number of acquisitions

        Returns:
            bool: The digitizer samples per second
        '''
        # ats310 = self._digitizers[prm_id]
        # return ats310.get_number_acquisitions()
        return self._prm_digitizer.get_number_acquisitions(prm_id)

    def get_n_repetitions(self, prm_id=1):
        '''
        Returns the number of repetitions currently set
        '''
        return self._repetitions[prm_id]

    def set_n_repetitions(self, prm_id, repetitions):
        '''
        Sets the number of repetitions
        '''
        self._repetitions[prm_id] = repetitions
        self._logger.info(f'Number of repetitions for PrM {prm_id} set to {self._repetitions[prm_id]}')

    def retrieve_run_numbers(self):
        '''
        Retrieves the latest run number from file
        '''
        if self._data_files_path is None:
            self._logger.warning('Cannot retrieve run number as data_files_path is not set.')
            return

        if not os.path.exists(self._data_files_path):
            self._logger.error(f'data_files_path {self._data_files_path} is not a real path.')
            raise RuntimeError()

        run_file_name = self._data_files_path + '/latest_run_number.txt'

        if not os.path.exists(run_file_name):
            self._logger.info('Latest run file doesnt exist.')
            for key in self._run_numbers:
                self._run_numbers[key] = -1
            self.write_run_numbers()
        else:
            with open(run_file_name, encoding="utf-8") as run_file:
                for line in run_file:
                    prm_id = line.split()[0]
                    run_no = line.split()[1]
                    print('PrM:', prm_id, 'Run No:', run_no)
                    self._run_numbers[int(prm_id)] = int(run_no)

    def write_run_numbers(self):
        '''
        Writes run numbers to file
        '''
        run_file_name = self._data_files_path + '/latest_run_number.txt'
        with open(run_file_name, "w", encoding="utf-8") as file:
            for key, value in self._run_numbers.items():
                file.write(str(key) + ' ' + str(value) + '\n')

    def increment_run_number(self, prm_id):
        '''
        Increments the run number by 1 and writes it to file
        '''
        self._run_numbers[prm_id] += 1
        self.write_run_numbers()

    def heartbeat(self):
        '''
        Writes a timestamp number in heartbeat.txt in the data
        file directory.
        '''
        if self._data_files_path is None:
            return

        timestamp = time.time()

        heartbeat_file_name = self._data_files_path + '/heartbeat.txt'

        with open(heartbeat_file_name, "w", encoding="utf-8") as file:
            file.write(str(timestamp))


    def get_run_number(self, prm_id):
        '''
        Returns the current run number
        '''
        return self._run_numbers[prm_id]


    def start_io_thread(self, prm_id):
        '''
        Starts the thread.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        worker = Worker(self.capture_data, prm_id=prm_id)
        # worker.signals.result.connect(self._result_callback)
        worker.signals.finished.connect(self._thread_complete)
        worker.signals.progress.connect(self._thread_progress)
        worker.signals.data.connect(self._thread_data)
        # worker.setAutoDelete(False)

        self._threadpool.start(worker)
        self._logger.info(f'Thread started for prm_id {prm_id}.')


    def capture_data(self, prm_id, progress_callback=None, data_callback=None):
        '''
        Capture the data. If running without a GUI, do not pass the progress_callback.

        Args:
            prm_id (int): The purity monitor ID.
            progress_callback (fn): The callback function to be called to show progress (optional)
        Returns:
            dict: A dictionary containing the prm_id, the status,
            the data for ch A, the data for ch B NO LONGER USED
        '''

        self._prm_digitizer.lamp_frequency(10, prm_id)
        self._prm_digitizer.lamp_on(prm_id)


        #
        # Wait some time for the HV to stabilize
        #
        purity_mon_wake_time = 4 # seconds
        self._logger.info(f'Awaking {prm_id} for {purity_mon_wake_time} seconds.')
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
        data_raw_combined = {
            'A': [],
            'B': []
        }

        for rep in range(self._repetitions[prm_id]):
            self._logger.info(f'*** Repetition number {rep}.')
            self._logger.info('Start capture for  {prm_id}.')
            self._prm_digitizer.start_capture(prm_id)
            self._logger.info(f'Check capture for  {prm_id}.')
            status = self._prm_digitizer.check_capture(prm_id)

            progress_callback.emit(prm_id, 'Retrieving Data', 100)
            data_raw = self._prm_digitizer.get_data(prm_id)

            for k in data_raw.keys():
                if k == '1':
                    data_raw[k] = [data_raw[k]]
                    data_raw['A'] = data_raw[k]
                    del data_raw[k]
                if k == '2':
                    data_raw[k] = [data_raw[k]]
                    data_raw['B'] = data_raw[k]
                    del data_raw[k]

            # Combine data in case we are doing multiple repetitions
            data_raw_combined['A'] = data_raw_combined['A'] + data_raw['A']
            data_raw_combined['B'] = data_raw_combined['B'] + data_raw['B']

        # Pack all the data in a dictionary
        data = {
            'prm_id': prm_id,
            'status': status,
            'time': datetime.datetime.today(),
            'A': data_raw_combined['A'],
            'B': data_raw_combined['B'],
        }

        # Send the data for saving
        data_callback.emit(data)

        self._prm_digitizer.lamp_off(prm_id)

        # Not used
        return data


    def _thread_data(self, data):
        '''
        This method is called at the end of every thread and receives the acquired data.

        Args:
            data (dict): The acquired data.
        '''
        print('***************Got data:', data['prm_id'])

        if data['status']:
            self._data[data['prm_id']] = {
                'A': data['A'],
                'B': data['B'],
                'time': data['time'],
            }
            self.save_data(data['prm_id'])
            print('Saved data.')


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
        self._logger.info(f'Thread completed for prm_id {prm_id}.')
        # self._window.start_stop_prm(prm_id)

        if status:
            self._window.reset_progress(prm_id, name='Done!', color='#006400') # dark green
        else:
            self._window.reset_progress(prm_id, name='Failed!', color='#B22222') # firebrick

        QTimer.singleShot(3000, lambda: self._window.reset_progress(prm_id))

        self._is_running[prm_id] = False


    def save_data(self, prm_id=1):
        '''
        Saves the most recent captured data, if any.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        # pylint: disable=invalid-name
        self.increment_run_number(prm_id)

        if self._data_files_path is None:
            self._logger.warning('Cannot save to file, data_files_path not set.')
            return
        if not self._save_as_npz and not self._save_as_txt:
            self._logger.warning('Not saving to file, neither save_as_npz or save_as_txt are set')
            return

        out_dict = {}

        timestr = time.strftime("%Y%m%d-%H%M%S")

        if self._data[prm_id] is None:
            return

        for ch in self._data[prm_id].keys():
            out_dict[f'ch_{ch}'] = self._data[prm_id][ch]

        if self._hv_on:
            hv_status = 'on'
        else:
            hv_status = 'off'

        out_dict['run'] = self._run_numbers[prm_id]
        out_dict['date'] = timestr
        out_dict['hv'] = hv_status
        out_dict['comment'] = self._comment

        out_dict['hv_anode'] = self._hv_control.get_hv_sense_value('anode', prm_id)
        out_dict['hv_anodegrid'] = self._hv_control.get_hv_sense_value('anodegrid', prm_id)
        out_dict['hv_cathode'] = self._hv_control.get_hv_sense_value('cathode', prm_id)

        # out_dict['samples_per_sec'] = self._digitizers[prm_id].get_samples_per_second()
        # out_dict['pre_trigger_samples'] = self._digitizers[prm_id].get_pre_trigger_samples()
        # out_dict['post_trigger_samples'] = self._digitizers[prm_id].get_post_trigger_samples()
        # out_dict['input_range_volts'] = self._digitizers[prm_id].get_input_range_volts()

        out_dict['samples_per_sec'] = self._prm_digitizer.get_samples_per_second(prm_id)
        out_dict['pre_trigger_samples'] = self._prm_digitizer.get_pre_trigger_samples(prm_id)
        out_dict['post_trigger_samples'] = self._prm_digitizer.get_post_trigger_samples(prm_id)
        out_dict['input_range_volts'] = self._prm_digitizer.get_input_range_volts(prm_id)

        # Add the extra configuration
        configs = self._window.get_config_values(prm_id)
        if configs is not None:
            for k, v in configs.items():
                out_dict['config_' + k] = v

        run_name = (
            'sbnd_prm' + str(prm_id) +
            '_run_' + str(self._run_numbers[prm_id]) +
            '_data_' +
            timestr
        )

        if self._save_as_npz:
            np.savez(os.path.join(self._data_files_path, run_name + '.npz'), **out_dict)

        if self._save_as_txt:
            file_name = os.path.join(self._data_files_path, run_name + '.txt')
            with open(file_name, 'w', encoding='utf-8') as f:
                for k, v in out_dict.items():
                    if isinstance(v, list):
                        v = np.stack(v) # assuming list of arrays
                        v_str = str(v.tolist()).replace(" ", "")
                        f.write(k + '=' + v_str + '\n')
                    else:
                        f.write(k + '=' + str(v) + '\n')


    def set_comment(self, comment):
        '''
        Sets a comment that will appear in the output file
        '''
        self._comment = comment


    def is_running(self, prm_id):
        '''
        Returns True if run is ongoing for prm_id
        '''
        return self._is_running[prm_id]


    def start_prm(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the PrM ON
        and starts the thread for the data acquisition.
        If no GUI is present, the thread is not started.

        Args:
            prm_id (int): The purity monitor ID.
        '''

        self._is_running[prm_id] = True

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


    def hv_on(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the HV ON.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._hv_control.hv_on(prm_id)
        self._hv_on = True


    def hv_off(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the HV OFF.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._hv_control.hv_off(prm_id)
        self._hv_on = False


    def set_mode(self, prm_id, mode):
        '''
        Sets the mode (auto, manual).

        Args:
            prm_id (int): The purity monitor ID.
            mode (int): The desired mode.
        '''
        self._mode = mode
        self._logger.info(f'Setting mode to: {self._mode}')

        if self._mode == 'auto':
            self._window.set_start_button_status(prm_id, False)
            self.periodic_start_prm(prm_id)
        elif self._mode == 'manual':
            self._timer.stop()

            # Wait until we have done running
            while self._is_running[prm_id]:
                time.sleep(0.1)

            self._window.set_start_button_status(prm_id, True)


    def periodic_start_prm(self, prm_id=1, time_interval=300):
        '''
        Starts purity monitor prm_id every time_interval seconds.
        Time interval cannot be less than 60 seconds, and if so,
        it will be set to 60 seconds.

        Args:
            prm_id (int): The purity monitor ID.
            time_interval (int): The time interaval in seconds.
        '''
        time_interval = max(time_interval, 60)

        self._window.set_start_button_status(prm_id, False)

        self._timer.timeout.connect(lambda: self.start_prm(prm_id))
        self._timer.start(time_interval * 1000)



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
            float: The anodegrid HV.
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
            bool: Whether the anodegrid HV is on or not.
        '''
        cathode_hv = self._hv_control.get_hv_status('cathode', prm_id)
        anode_hv = self._hv_control.get_hv_status('anode', prm_id)
        anodegrid_hv = self._hv_control.get_hv_status('anodegrid', prm_id)

        return cathode_hv, anode_hv, anodegrid_hv
