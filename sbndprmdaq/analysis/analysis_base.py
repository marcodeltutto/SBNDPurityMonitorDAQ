'''
Contains PrM analysis base class
'''

from abc import ABC, abstractmethod

import numpy as np

#pylint: disable=invalid-name,too-many-instance-attributes,too-many-arguments,consider-using-f-string,invalid-unary-operand-type,too-many-return-statements,bare-except,multiple-statements,dangerous-default-value,too-many-lines,broad-exception-caught,arguments-differ
class PrMAnalysisBase(ABC):
    '''
    Base class for PrM signal analysis.
    '''

    _volt_to_mv = 1e3
    _sec_to_us = 1e6
    _us_to_ms = 1e-3
    _RC = 119

    def __init__(
        self,
        wf_c, wf_a,
        samples_per_sec=2e6, config={},
        wf_c_hvoff=None,
        wf_a_hvoff=None,
        remove_breakdown=False,
        debug=True
    ):
        '''
        Constructor.

        Args:
            wf_c (list): cathode waveforms
            wf_a (list): anode waveforms
            samples_per_sec (int): number of samples per seconds
            config (dict): configuration
            wf_c_hvoff (list): HV off cathode waveforms
            wf_a_hvoff (list): HV on cathode waveforms
        '''

        self._raw_wf_x = np.arange(len(wf_c[0])) / samples_per_sec * self._sec_to_us # us
        self._raw_wf_c = np.mean(wf_c, axis=0) * self._volt_to_mv
        self._raw_wf_a = np.mean(wf_a, axis=0) * self._volt_to_mv

        self._wf_c = None
        self._wf_a = None
        self._wf_x = None

        self._qa = None
        self._qc = None

        self._td = None
        self._tau = None

        self._err = 0

        self._debug = debug

        if wf_c_hvoff is not None and wf_a_hvoff is not None:
            if len(wf_c_hvoff) and len (wf_a_hvoff):
                if self._debug: print('Subtracting HV OFF')
                self._raw_wf_c -= np.mean(wf_c_hvoff, axis=0) * self._volt_to_mv
                self._raw_wf_a -= np.mean(wf_a_hvoff, axis=0) * self._volt_to_mv

        self._deltat_start_c = config.get('deltat_start_c', 450)
        self._deltat_start_a = config.get('deltat_start_a', 900)
        self._trigger_sample = config.get('trigger_sample', 512)
        self._signal_range_c = config.get('signal_range_c', [310, 500])
        self._signal_range_a = config.get('signal_range_a', [600, 1000])
        self._baseline_range_c = config.get('baseline_range_c', [0, 450])
        self._baseline_range_a = config.get('baseline_range_a', [2000, 2400])
        self._plot_range = config.get('plot_range', [0, 3500])
        self._plot_title = config.get('title', 'PrM')

        if remove_breakdown:

            if self._debug: print('Removing waveforms that may suffer from breakdown')

            new_cathode = []
            new_anode = []

            for i, cathode, anode in enumerate(zip(wf_c, wf_a)):
                if all(cathode[600:] * self._volt_to_mv < 20) and all(cathode[600:] * self._volt_to_mv > -20):
                    new_cathode.append(cathode)

                if all(anode[600:] * self._volt_to_mv < 20) and all(anode[600:] * self._volt_to_mv > -20):
                    new_anode.append(anode)

            if self._debug:  print(f'Using only {len(new_cathode)} of the {len(wf_c)} cathode waveforms.')
            if self._debug:  print(f'Using only {len(new_anode)} of the {len(wf_a)} anode waveforms.')

            self._raw_wf_c = np.mean(np.array(new_cathode), axis=0)
            self._raw_wf_a = np.mean(np.array(new_anode), axis=0)

        if len(self._raw_wf_c) == 6000:
            self._signal_range_c = [i * 2 for i in self._signal_range_c]
            self._signal_range_a = [i * 2 for i in self._signal_range_a]

    @abstractmethod
    def calculate(self):
        '''
        Performs all the calculation
        '''

    @abstractmethod
    def plot_summary(self, container=None, savename=None):
        '''
        Generates a summary plot

        Args:
            container (dict): data container to add info on plot
            savename (string): full path to save file
        '''

    def get_lifetime(self, unit='us'):
        '''
        Returns the lifetime in the specified units
        '''
        if self._tau is None:
            return -2

        if self._tau < 0:
            return self._tau

        if unit == 'us':
            return self._tau

        if unit == 'ms':
            return self._tau * 1e-3

        print(f'Unit {unit} not supported')

        return -999

    def get_drifttime(self, unit='us'):
        '''
        Returns the drifttime in the specified units
        '''
        if self._td is None:
            return -2

        if self._td < 0:
            return self._td

        if unit == 'us':
            return self._td

        if unit == 'ms':
            return self._td * 1e-3

        print(f'Unit {unit} not supported')

        return -999

    def get_qa(self, unit='mV'):
        '''
        Returns the Qa in the specified units
        '''
        if self._qa is None:
            return -2

        if self._qa < 0:
            return self._qa

        if unit == 'mV':
            return self._qa

        print(f'Unit {unit} not supported')

        return -999

    def get_qc(self, unit='mV'):
        '''
        Returns the Qc in the specified units
        '''
        if self._qc is None:
            return -2

        if self._qc < 0:
            return self._qc

        if unit == 'mV':
            return self._qc

        print(f'Unit {unit} not supported')

        return -999

    def _process_error(self, status):
        '''
        Base on the error (if any) adds and error code to lifetime
        '''
        code = 0
        if status == 'no_anode':
            code = -10
        elif status == 'no_cathode':
            code = -11
        elif status == 'cathode_deltat_large':
            code = -12
        elif status == 'anode_deltat_large':
            code = -13
        elif status == 'qa_lt_qc':
            code = -14
        elif status == 'fit_failed':
            code = -20
        elif status == 'deltat_negative':
            code = -21
        else:
            code = -99

        if code != 0:
            self._tau = code
            self._td = -1
            self._qa = -1
            self._qc = -1
