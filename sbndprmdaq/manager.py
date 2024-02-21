'''
The purity monitor manager.
'''
import os
import time
import datetime
import logging
import numpy as np
import epics

from PyQt5.QtCore import QThreadPool, QTimer

from sbndprmdaq.data_storage import DataStorage
from sbndprmdaq.analysis import PrMAnalysis
from sbndprmdaq.threading_utils import Worker
from sbndprmdaq.digitizer.prm_digitizer import PrMDigitizer
from sbndprmdaq.high_voltage.hv_control_mpod import HVControlMPOD

#pylint: disable=too-many-public-methods,too-many-branches,too-many-statements,too-many-locals
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
        self._take_hvoff_run = {}
        self._mode = {}
        self._meas = {}
        self._time_interval = {}
        self._timer = {}

        self._data_files_path = config['data_files_path']
        self._save_as_npz = config['save_as_npz']
        self._save_as_txt = config['save_as_txt']

        for prm_id in config['prm_ids']:
            self._data[prm_id] = None
            self._is_running[prm_id] = False
            self._run_numbers[prm_id] = None
            self._repetitions[prm_id] = 1
            self._take_hvoff_run[prm_id] = True
            self._mode[prm_id] = 'manual'
            self._meas[prm_id] = None
            self._time_interval[prm_id] = self._window._prm_controls[prm_id]._interval_spinbox.value() * 60
            self._timer[prm_id] = QTimer()

        self._set_digitizer_and_hv(config)

        self._logger.info(f'Number of available digitizers: {self._prm_digitizer.n_digitizers()}')

        self._hv_on = False
        self._use_hv = True

        self._threadpool = QThreadPool()
        self._logger.info(f'Number of available threads: {self._threadpool.maxThreadCount()}')

        self._prm_id_bounded = {}
        for bounded_id, main_id in config['bound_prms'].items():
            if self._window is not None:
                self._window.disable_controls(bounded_id)
            self._prm_id_bounded[main_id] = bounded_id


        self._do_store = config['data_storage']
        self._data_storage = DataStorage(config)

        self._do_analyze = config['analyze']

        self._comment = 'No comment'

        self._config = config

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
                    self._logger.info(f'PrM: {prm_id} Run No: {run_no}')
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


    def check_hv_range(self, prm_id):
        '''
        Checks if the HV is whitin a range

        Return:
            bool: False is HV is outside of allowed range
        '''
        ret = self._hv_control.check_hv_range(prm_id)

        # self._logger.warning('HV value is outside of allowed range!')

        return ret


    def start_thread(self, prm_id):
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

        self._logger.info(f'About to start thread for prm_id {prm_id}.')
        self._threadpool.start(worker)
        self._logger.info(f'Thread started for prm_id {prm_id}.')

    def _lamp_on(self, prm_ids):

        for prm_id in prm_ids:

            self._is_running[prm_id] = True

            self._logger.info(f'Turning flash lamp on for PrM {prm_id}.')
            self._prm_digitizer.lamp_frequency(2, prm_id)
            self._prm_digitizer.lamp_on(prm_id)


    def _lamp_off(self, prm_ids):

        for prm_id in prm_ids:

            self._is_running[prm_id] = False

            self._logger.info(f'Turning flash lamp off for PrM {prm_id}.')
            self._prm_digitizer.lamp_off(prm_id)

    def _turn_hv_on(self, prm_ids):

        for prm_id in prm_ids:

            self._logger.info(f'Turning HV on for PrM {prm_id}.')
            self._hv_control.hv_on(prm_id)
            self.check_hv_range(prm_id)


        # Wait for HV to stabilize
        for prm_id in prm_ids:
            wait_time_max = 120 # seconds
            start = time.time()
            while not self._hv_control.hv_stable(prm_id):
                time.sleep(2)

                if wait_time_max < time.time() - start:
                    break


    def _turn_hv_off(self, prm_ids):

        for prm_id in prm_ids:

            self._logger.info(f'Turning HV off for PrM {prm_id}.')
            self._hv_control.hv_off(prm_id)

    def _take_data(self, prm_id, progress_callback=None):
        '''
        Takes the actual data
        '''

        data_raw_combined = {
            'A': [],
            'B': [],
            'C': [],
            'D': []
        }

        for rep in range(self._repetitions[prm_id]):
            self._logger.info(f'*** Repetition number {rep}.')
            self._logger.info(f'Start capture for {prm_id}.')
            self._prm_digitizer.start_capture(prm_id)
            self._logger.info(f'Check capture for {prm_id}.')
            status = self._prm_digitizer.check_capture(prm_id)

            progress_callback.emit(prm_id, 'Retrieving Data', 100)
            data_raw_ = self._prm_digitizer.get_data(prm_id)

            print('PPPPPPPPPP')
            print('len(data_raw_)', len(data_raw_))
            if 1 in data_raw_:
                print(len(data_raw_[1]))
                print('len(data_raw_[1])', len(data_raw_[1]))

            data_raw = {}

            for k in data_raw_.keys():
                if k == '1':
                    data_raw['A'] = data_raw_[k]
                elif k == '2':
                    data_raw['B'] = data_raw_[k]
                elif k == '3':
                    data_raw['C'] = data_raw_[k]
                elif k == '4':
                    data_raw['D'] = data_raw_[k]
                else:
                    data_raw[k] = data_raw_[k]

            # Combine data in case we are doing multiple repetitions
            data_raw_combined['A'] = data_raw_combined['A'] + data_raw['A']
            data_raw_combined['B'] = data_raw_combined['B'] + data_raw['B']
            data_raw_combined['C'] = data_raw_combined['C'] + data_raw['C']
            data_raw_combined['D'] = data_raw_combined['D'] + data_raw['D']

        return data_raw_combined, status


    def _prm_wait(self, prm_id, purity_mon_wake_time=4, progress_callback=None):
        '''
        Waits for purity_mon_wake_time seconds and communicated this to the GUI
        '''
        self._logger.info(f'Awaking {prm_id} for {purity_mon_wake_time} seconds.')
        start = time.time()
        while purity_mon_wake_time > time.time() - start:
            perc = (time.time() - start) / purity_mon_wake_time * 100
            if progress_callback is not None:
                progress_callback.emit(prm_id, 'Awake Monitor', perc)
            time.sleep(0.1)



    def capture_data(self, prm_id, progress_callback=None, data_callback=None):
        '''
        Capture the data. If running without a GUI, do not pass the progress_callback.

        Args:
            prm_id (int): The purity monitor ID.
            progress_callback (fn): The callback function to be called to show progress (optional)
        Returns:
            dict: A dictionary containing the prm_ids processed, and the statuses
        '''

        prm_ids = [prm_id]
        if prm_id in self._prm_id_bounded:
            prm_ids.append(self._prm_id_bounded[prm_id])

        data_hv_off = {'A': [], 'B': [], 'C': [], 'D': []}
        data_hv_on  = {'A': [], 'B': [], 'C': [], 'D': []}

        #
        # First run with no HV
        #
        if self._take_hvoff_run[prm_id]:

            if progress_callback is not None:
                progress_callback.emit(prm_id, 'NO HV run', 50)

            time.sleep(1)

            self._logger.info(f'NO HN Run for {prm_id}.')

            self._lamp_on(prm_ids)

            data_hv_off, _ = self._take_data(prm_id, progress_callback)

            self._lamp_off(prm_ids)

            self._logger.info(f'NO HN Run for {prm_id} completed.')


        if progress_callback is not None:
            progress_callback.emit(prm_id, 'Wait for HV', 0)


        #
        # Second run with HV
        #
        self._turn_hv_on(prm_ids)
        self._prm_wait(prm_id, 4, progress_callback)
        self._lamp_on(prm_ids)

        if progress_callback is not None:
            progress_callback.emit(prm_id, 'Start Capture', 100)

        data_hv_on, status = self._take_data(prm_id, progress_callback)

        # Pack all the data in a dictionary
        data = {
            'prm_id': prm_id,
            'status': status,
            'time': datetime.datetime.today(),
            'A': data_hv_on['A'],
            'B': data_hv_on['B'],
            'A_nohv': data_hv_off['A'],
            'B_nohv': data_hv_off['B'],
        }

        # Send the data for saving
        data_callback.emit(data)

        if prm_id in self._prm_id_bounded:
            data = {
                'prm_id': self._prm_id_bounded[prm_id],
                'status': status,
                'time': datetime.datetime.today(),
                'A': data_hv_on['C'],
                'B': data_hv_on['D'],
                'A_nohv': data_hv_off['C'],
                'B_nohv': data_hv_off['D'],
            }

            # Send the data for saving
            data_callback.emit(data)

        self._lamp_off(prm_ids)
        time.sleep(2)
        self._turn_hv_off(prm_ids)


        ret = {
            'prm_ids': prm_ids,
            'statuses': [status] * len(prm_ids),
        }

        return ret


    def _thread_data(self, data):
        '''
        This method is called at the end of every thread and receives the acquired data.

        Args:
            data (dict): The acquired data.
        '''
        self._logger.info(f'Got data for PrM {data["prm_id"]}.')

        if data['status']:
            self._data[data['prm_id']] = {
                'A': data['A'],
                'B': data['B'],
                'A_nohv': data['A_nohv'],
                'B_nohv': data['B_nohv'],
                'time': data['time'],
            }
            out_dict = self.save_data(data['prm_id'])
            if out_dict is not None:
                self.output_to_epics(data['prm_id'], out_dict)
            self._logger.info(f'Saved data for PrM {data["prm_id"]}.')
        else:
            self._logger.info(f'Bad capture, no data to save for PrM {data["prm_id"]}.')


    def _thread_progress(self, prm_id, name, progress):
        '''
        Callback called during a thread to show progress.

        Args:
            prm_id (int): The purity monitor ID.
            name (str): The name of the current task for display.
            progress (int): The progress (0 to 100 percent).
        '''
        self._window.set_progress(prm_id=prm_id, name=name, perc=progress)
        if prm_id in self._prm_id_bounded:
            self._window.set_progress(prm_id=self._prm_id_bounded[prm_id], name=name, perc=progress)


    def _thread_complete(self, prm_ids, statuses):
        '''
        Called when a thread ends.

        Args:
            prm_ids (list if int): The purity monitor IDs.
            statuses (list bool): True is the acquisition suceeded, False otherwise.
        '''

        for prm_id, status in zip(prm_ids, statuses):
            self._logger.info(f'Thread completed for prm_id {prm_id}. Status: {status}.')

            if status:
                self._window.reset_progress([prm_id], name='Done!', color='#006400') # dark green
            else:
                self._window.reset_progress([prm_id], name='Failed!', color='#B22222') # firebrick

            self._is_running[prm_id] = False


        QTimer.singleShot(3000, lambda: self._window.reset_progress(prm_ids))



    def save_data(self, prm_id=1):
        '''
        Saves the most recent captured data, if any.

        Args:
            prm_id (int): The purity monitor ID.

        Returns:
            out_dict (dict): Saved data.
        '''
        # pylint: disable=invalid-name
        self._logger.info(f'Saving data for PrM {prm_id}.')

        self.increment_run_number(prm_id)

        if self._data_files_path is None:
            self._logger.warning('Cannot save to file, data_files_path not set.')
            return None
        if not self._save_as_npz and not self._save_as_txt:
            self._logger.warning('Not saving to file, neither save_as_npz or save_as_txt are set')
            return None

        out_dict = {}

        timestr = time.strftime("%Y%m%d-%H%M%S")

        if self._data[prm_id] is None:
            return None

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
        # out_dict['input_range_volts'] = self._prm_digitizer.get_input_range_volts(prm_id)

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

        saved_files = []

        if self._save_as_npz:
            file_name = os.path.join(self._data_files_path, run_name + '.npz')
            saved_files.append(file_name)
            np.savez(saved_files[-1], **out_dict)

        if self._save_as_txt:
            file_name = os.path.join(self._data_files_path, run_name + '.txt')
            saved_files.append(file_name)
            with open(file_name, 'w', encoding='utf-8') as f:
                for k, v in out_dict.items():
                    if isinstance(v, list):
                        v = np.stack(v) # assuming list of arrays
                        v_str = str(v.tolist()).replace(" ", "")
                        f.write(k + '=' + v_str + '\n')
                    else:
                        f.write(k + '=' + str(v) + '\n')

        # Analyze data
        self._meas[prm_id] = None
        if self._do_analyze:
            # try:
            #pylint: disable=protected-access,attribute-defined-outside-init,broad-exception-caught
            self._logger.info(f'Analyzing data for PrM {prm_id}.')
            ana_config = self._config['analysis_config'][prm_id]
            self._prmana = PrMAnalysis(out_dict['ch_A'], out_dict['ch_B'],
                                       config=ana_config,
                                       wf_c_hvoff=out_dict['ch_A_nohv'], wf_a_hvoff=out_dict['ch_B_nohv'])
            self._prmana.calculate()
            file_name = os.path.join(self._data_files_path, run_name + '_ana.png')
            self._prmana.plot_summary(container=out_dict, savename=file_name)
            self._meas[prm_id] = {
                'td': self._prmana.get_drifttime(unit='ms'),
                'qc': self._prmana.get_qc(unit='mV'),
                'qa': self._prmana.get_qa(unit='mV'),
                'tau': self._prmana.get_lifetime(unit='ms')
            }
            saved_files.append(file_name)
            # except Exception as err:
            #     self._logger.warning('PrMAnalysis failed:')
            #     self._logger.warning(type(err))
            #     self._logger.warning(err)


        # Copy data to sbndgpvm
        if self._do_store:
            self._logger.info(f'Storing data for PrM {prm_id}.')
            self._data_storage.store_files(saved_files)


        self._logger.info(f'Data saved for PrM {prm_id}.')

        return out_dict

    #pylint: disable=invalid-name
    def output_to_epics(self, prm_id, out_dict):
        '''
        Updates EPICS with run data.

        Args:
            prm_id (int): The purity monitor ID.
            out_dict (dict): Data from run.
        '''
        if prm_id == 1:
            prm = 'tpclong'
        elif prm_id == 2:
            prm = 'tpcshort'
        elif prm_id == 3:
            prm = 'inline'
        else:
            raise ValueError(f'prm_id {prm_id} invalid')

        res = []
        for item in ['cathode', 'anodegrid', 'anode']:
            res.append(epics.caput(f'sbnd_prm_{prm}_hv/{item}_voltage', out_dict[f'hv_{item}']))

        res.append(epics.caput(f'sbnd_prm_{prm}_signal/drift_time', self._meas[prm_id]['td']))
        res.append(epics.caput(f'sbnd_prm_{prm}_signal/lifetime', self._meas[prm_id]['tau']))
        res.append(epics.caput(f'sbnd_prm_{prm}_signal/QA', self._meas[prm_id]['qa']))
        res.append(epics.caput(f'sbnd_prm_{prm}_signal/QC', self._meas[prm_id]['qc']))

        if all(res):
            self._logger.info(f'All EPICS updates successful for PrM {prm_id}')
        elif any(res):
            self._logger.info(f'Some EPICS updates failed for PrM {prm_id}')
        else:
            self._logger.info(f'All EPICS updates failed for PrM {prm_id}')

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


    # def start_prm(self, prm_id=1):
    #     '''
    #     Starts prm_id and also all the other PrMs
    #     bounded to it.

    #     Args:
    #         prm_id (int): The purity monitor ID.
    #     '''
    #     prm_ids = [prm_id]

    #     if prm_id in self._prm_id_bounded:
    #         prm_ids.append(self._prm_id_bounded[prm_id])

    #     for pm_id in prm_ids:
    #         self.start_single_prm(pm_id)


    def start_prm(self, prm_id=1):
        '''
        Starts the thread for running prm_id.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._is_running[prm_id] = True

        if self._window is not None:
            # Start a thread where we let the digitizer run
            self.start_thread(prm_id)
        else:
            self.capture_data(prm_id)


    def stop_prm(self, prm_id=1):
        '''
        Not implemented.

        Args:
            prm_id (int): The purity monitor ID.
        '''


    def hv_on(self, prm_id=1):
        '''
        Turns on the HV.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._hv_control.hv_on(prm_id)
        self._hv_on = True


    def hv_off(self, prm_id=1):
        '''
        Turns off the HV.

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
        self._mode[prm_id] = mode
        self._logger.info(f'Setting mode to: {self._mode[prm_id]}')

        if self._mode[prm_id] == 'auto':
            self._window.set_start_button_status(prm_id, False)
            self.periodic_start_prm(prm_id)
        elif self._mode[prm_id] == 'manual':
            self._timer[prm_id].stop()

            # Wait until we have done running
            while self._is_running[prm_id]:
                time.sleep(0.1)

            self._window.set_start_button_status(prm_id, True)

    def set_interval(self, prm_id, interval):
        '''
        Sets the time interval to use in automatic mode.
        Time interval cannot be less than 60 seconds, and if so,
        it will be set to 300 seconds.

        Args:
            prm_id (int): The purity monitor ID.
            interval (int): The time interval in minutes.
        '''
        self._time_interval[prm_id] = max(interval, 300)
        self._logger.info(f'Time interval set to {self._time_interval[prm_id]} for PrM {prm_id}.')


    def remaining_time(self, prm_id):
        '''
        Returns the remaining time on the timer

        Args:
            prm_id (int): The purity monitor ID.
        '''
        return self._timer[prm_id].remainingTime()


    def take_hvoff_run(self, prm_id, do_take):
        '''
        Saves option to take run with no HV or not.

        Args:
            prm_id (int): The purity monitor ID.
            do_take (bool): True if need to take HV off run.
        '''
        self._take_hvoff_run[prm_id] = do_take
        self._logger.info(f'Taking HV off run for {prm_id}?: {self._take_hvoff_run[prm_id]}')



    def periodic_start_prm(self, prm_id=1):
        '''
        Starts purity monitor prm_id every time_interval seconds.
        Time interval cannot be less than 60 seconds, and if so,
        it will be set to 300 seconds.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        time_interval = self._time_interval[prm_id]

        self._window.set_start_button_status(prm_id, False)

        self._timer[prm_id].timeout.connect(lambda: self.start_prm(prm_id))
        self._timer[prm_id].start(time_interval * 1000)


    def get_data(self, prm_id):
        '''
        Sets the mode (auto, manual).

        Args:
            prm_id (int): The purity monitor ID.

        Returns:
            dict: A dictionary containing the data for ch A and for ch B.
        '''
        return self._data[prm_id]

    def get_latest_lifetime(self, prm_id):
        '''
        Returns the Qa, Qc, tau from the latest data.

        Args:
            prm_id (int): The purity monitor ID.

        Returns:
            float: The extracted Qa.
            float: The extracted Qc.
            float: The extracted Lifetime.
        '''
        if self._meas[prm_id] is not None:
            return self._meas[prm_id]['qa'], self._meas[prm_id]['qc'], self._meas[prm_id]['tau']

        return -999, -999, -999


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
