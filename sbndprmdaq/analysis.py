'''
Contains PrM analysis class
'''

import datetime
import subprocess
import numpy as np

import matplotlib.pyplot as plt

#pylint: disable=invalid-name,too-many-instance-attributes,too-many-arguments,consider-using-f-string,invalid-unary-operand-type,too-many-return-statements,bare-except,multiple-statements

class PrMAnalysis:
    '''
    A class to perform quick PrM analysis
    '''

    _volt_to_mv = 1e3
    _sec_to_us = 1e6
    _us_to_ms = 1e-3

    def __init__(self, wf_c, wf_a, samples_per_sec=2e6, config=None, wf_c_hvoff=None, wf_a_hvoff=None, debug=True):
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

        self._baseline_c = None
        self._baseline_rms_c = None
        self._baseline_a = None
        self._baseline_rms_a = None

        self._time_start_c = None
        self._time_end_c = None
        self._deltat_c = None

        self._time_start_a = None
        self._time_end_a = None
        self._deltat_a = None

        self._max_c = None
        self._max_a = None

        self._qa = None
        self._qc = None

        self._td = None
        self._tau = None

        self._offset = None

        self._err = 0

        self._debug = debug

        if wf_c_hvoff is not None and wf_a_hvoff is not None:
            if len(wf_c_hvoff) and len (wf_a_hvoff):
                if self._debug: print('Subtracting HV OFF')
                self._raw_wf_c -= np.mean(wf_c_hvoff, axis=0) * self._volt_to_mv
                self._raw_wf_a -= np.mean(wf_a_hvoff, axis=0) * self._volt_to_mv


        if config is None:
            self._deltat_start_c = 450
            self._deltat_start_a = 900
            self._trigger_sample = 512 # When the flash lamp flashes
            self._baseline_range_c = [0,450]
            self._baseline_range_a = [2000,2400]
            self._plot_range = [0, 3500]
            self._plot_title = 'PrM'
        else:
            self._deltat_start_c = config['deltat_start_c']
            self._deltat_start_a = config['deltat_start_a']
            self._trigger_sample = config['trigger_sample']
            self._baseline_range_c = config['baseline_range_c']
            self._baseline_range_a = config['baseline_range_a']
            self._plot_range = config['plot_range']
            self._plot_title = config['title']


    def pre_process(self, smooth=True, n=10):
        '''
        Smooths the data if requested

        Args:
            smooth (bool): smooths the data if True
            n (int): smoothing level
        '''

        if smooth:
            self._wf_c = np.convolve(self._raw_wf_c, np.ones(n)/n, mode='valid')
            self._wf_a = np.convolve(self._raw_wf_a, np.ones(n)/n, mode='valid')
            self._wf_x = self._raw_wf_x[int(n/2):-int(n/2)+1]
            self._offset = int(n/2)
            self._trigger_sample -= self._offset
        else:
            self._wf_c = self._raw_wf_c
            self._wf_a = self._raw_wf_a
            self._wf_x = self._raw_wf_x

        return 'ok'

    def estimate_baseline(self):
        '''
        Baseline estimation

        Args:
            baseline_range_c (list): Range used to estimate baseline for cathode
            baseline_range_a (list): Range used to estimate baseline for anode
        '''
        self._baseline_c = np.mean(self._wf_c[self._baseline_range_c])
        # self._baseline_rms_c = np.std(self._wf_c[self._baseline_range_c])
        self._baseline_rms_c = np.std(self._raw_wf_c[self._baseline_range_c])

        self._baseline_a = np.mean(self._wf_a[self._baseline_range_a])
        # self._baseline_rms_a = np.std(self._wf_a[self._baseline_range_a])
        self._baseline_rms_a = np.std(self._raw_wf_a[self._baseline_range_a])

        if self._debug: print('Baseline estimated')
        return 'ok'


    def estimate_deltat(self):
        '''
        Delta t estimation
        '''

        # _trigger_sample += self._offset
        # _deltat_start_c -= self._offset
        # _deltat_start_a -= self._offset
        if self._debug: print('estimate_deltat')

        # Cathode
        try:
            tmp_wvf = self._wf_c[self._deltat_start_c:]
            min_idx = np.argmin(tmp_wvf)
            if self._debug: print('min_idx', min_idx)
            selected = tmp_wvf[0:min_idx]
            # print('->', selected, np.argwhere((selected-(base-base_rms))>0))
            if self._trigger_sample:
                start_idx = self._trigger_sample - self._deltat_start_c
            else:
                start_idx = np.argwhere((selected-(self._baseline_c-self._baseline_rms_c))>0)[-1]
            start = self._wf_x[start_idx + self._deltat_start_c]
            end = self._wf_x[min_idx + self._deltat_start_c]
            if self._debug: print('Cathode: start', start, 'end', end)
            self._time_start_c = start
            self._time_end_c = end
            self._deltat_c = end - start
        except:
            return 'deltat_cathode_failed'

        # Anode
        try:
            tmp_wvf = self._wf_a[self._deltat_start_a:]
            max_idx = np.argmax(tmp_wvf)
            selected = tmp_wvf[0:max_idx]

            # Find start of anode wf (when is 0.05% from the baseline)
            th = (selected[-1] - self._baseline_a) * 0.3
            start_idx = np.argwhere((selected-self._baseline_a)<th)[-1]
            start = self._wf_x[start_idx + self._deltat_start_a]
            end = self._wf_x[max_idx + self._deltat_start_a]
            if self._debug: print('Anode: start', start, 'end', end)
            self._time_start_a = start[0]
            self._time_end_a = end
            self._deltat_a = end - start[0]
        except:
            return 'deltat_cathode_failed'

        if self._debug: print('estimate_deltat done')
        return 'ok'


    def rc_correction(self, delta_t, RC=119):
        '''
        RC correction estimation

        Args:
            delta_t (float): rise time
            RC (float): RC time constant
        '''
        return (delta_t / RC) * (1 / (1 - np.exp(-delta_t/RC)))

    def calculate_lifetime(self):
        '''
        Lifetime estimation

        Args:
            start_idx (int): where to start estimation (to esclude lamp noise)
        '''

        self._max_c = np.min(self._wf_c[self._trigger_sample:])
        self._max_a = np.max(self._wf_a[self._trigger_sample:])

        if self._debug: print('Max: C', self._max_c, ', A', self._max_a)

        # self._max_c += self._baseline_rms_c
        # self._max_a -= self._baseline_rms_a

        rc_correction_c = self.rc_correction(self._deltat_c, RC=119)
        rc_correction_a = self.rc_correction(self._deltat_a, RC=119)

        if self._debug: print('RC correction: C', rc_correction_c, ', A', rc_correction_a)
        if self._debug: print('> Mac C', self._max_c, 'base c', self._baseline_c, 'rc', rc_correction_c)
        self._qc = (self._max_c - self._baseline_c) * rc_correction_c
        self._qa = (self._max_a - self._baseline_a) * rc_correction_a

        self._qc = np.abs(self._qc)
        if self._debug: print(type(self._max_a), type(self._baseline_a), type(rc_correction_a), type(self._qa))

        if self._debug: print('Qc', self._qc, ', QA', self._qa, 'Qa/Qc', self._qa/self._qc)

        self._td = self._time_end_a - self._time_start_c

        if self._debug: print('Drift time', self._td)

        self._tau = -self._td/np.log(self._qa/self._qc)

        if self._debug: print('Lifetime', self._tau, 'mus')

        return 'ok'


    def sanity_check(self):
        '''
        Checks values are sensible
        '''
        if np.abs((self._max_a - self._baseline_a) / (self._baseline_rms_a)) < 5:
            return 'no_anode'

        if self._max_a < 0:
            return 'no_anode'

        if np.abs((self._max_c - self._baseline_c) / (self._baseline_rms_a)) < 5:
            return 'no_cathode'

        if self._max_c > 0:
            return 'no_cathode'

        if self._deltat_c > 50:
            return 'cathode_deltat_large'

        if self._deltat_a > 50:
            return 'anode_deltat_large'

        if self._qa > self._qc:
            return 'qa_lt_qc'

        return 'ok'

    def process_error(self, status):
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
        elif code == 'anode_deltat_large':
            code = -13
        elif code == 'qa_lt_qc':
            code = -14
        else:
            code = -99

        if code != 0:
            self._tau = code
            self._td = -1
            self._qa = -1
            self._qc = -1


    def calculate(self):
        '''
        Performs all the calculation
        '''

        self._err = self.pre_process(smooth=True, n=40)

        if self._err != 'ok':
            return

        self._err = self.estimate_baseline()

        if self._err != 'ok':
            return

        self._err = self.estimate_deltat()

        if self._err != 'ok':
            return

        self._err = self.calculate_lifetime()

        if self._err != 'ok':
            return

        status = self.sanity_check()

        if status != 'ok':
            self.process_error(status)

    def get_lifetime(self, unit='us'):
        '''
        Returns the lifetime in the specified units
        '''
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
        if self._qc < 0:
            return self._qc

        if unit == 'mV':
            return self._qc

        print(f'Unit {unit} not supported')
        return -999


    def plot_summary(self, container=None, savename=None):
        '''
        Generates a summary plot

        Args:
            container (dict): data container to add info on plot
            savename (string): full path to save file
        '''
        if self._td is None:
            return None, None

        if self._td < 0:
            return None, None

        prop_cycle = plt.rcParams['axes.prop_cycle']
        _colors = prop_cycle.by_key()['color']

        fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(12, 8), sharex=True)
        fig.subplots_adjust(hspace=0)

        ax[0].plot(self._raw_wf_x, self._raw_wf_a, label='Anode Raw', color=_colors[0], alpha=0.5,)
        ax[1].plot(self._raw_wf_x, self._raw_wf_c, label='Cathode Raw', color=_colors[1], alpha=0.5)

        ax[0].plot(self._wf_x, self._wf_a, label='Anode', color=_colors[0])
        ax[1].plot(self._wf_x, self._wf_c, label='Cathode', color=_colors[1])


        ax[0].axhline(self._baseline_a, color=_colors[0],
                      label=f'Baseline = {self._baseline_a:.1f} ' + r'$\pm$' + f' {self._baseline_rms_a:.1f} mV', linestyle='dashed')
        ax[1].axhline(self._baseline_c, color=_colors[1],
                      label=f'Baseline = {self._baseline_c:.1f} ' + r'$\pm$' + f' {self._baseline_rms_c:.1f} mV', linestyle='dashed')


        ax[0].axvline(self._time_start_c, color='grey', linestyle='dashed')
        ax[1].axvline(self._time_start_c, color='grey', linestyle='dashed')
        ax[0].axvline(self._time_end_a, color='grey', linestyle='dashed')
        ax[1].axvline(self._time_end_a, color='grey', linestyle='dashed')

        ax[0].axvspan(self._time_start_a, self._time_end_a, alpha=0.5, color=_colors[0])
        ax[1].axvspan(self._time_start_c, self._time_end_c, alpha=0.5, color=_colors[1])

        ax[0].axhline(self._max_a, color=_colors[0], label=f'Max = {self._max_a:.1f} mV', linestyle='dashdot')
        ax[1].axhline(self._max_c, color=_colors[1], label=f'Max = {self._max_c:.1f} mV', linestyle='dashdot')

        x_plot_range = self._time_end_a * 2
        ax[0].set_xlim([0, x_plot_range])
        ax[1].set_xlim([0, x_plot_range])

        y_plot_range = np.abs(self._max_c) * 1.4
        ax[0].set_ylim([-29.99,        y_plot_range])
        ax[1].set_ylim([-y_plot_range, 29.99])

        ax[0].set_title(f'Drift time: {self._td/1e3:.2f} ' + r'$ms$'
                        + f'\nQa/Qc: {self._qa/self._qc:.2f}'
                        + f'\nLifetime: {self._tau/1e3:.2f} ' + r'$ms$',
                        loc='left', fontsize=12)

        self.set_lifetime_axis(ax, self._plot_title, container, text_pos=[0.015, 0.56])

        if savename:
            plt.savefig(savename)
        # plt.show()

        return fig, ax

    def set_lifetime_axis(self, ax, title, container=None, draw_txt=True, text_pos=None):
        '''
        Customizes the axis
        '''
        for a in ax:
            a.set_ylabel('Waveform [mV]',fontsize=18)
            a.set_xlabel('Time [us]',fontsize=18)
        #     a.set_title('SBND Purity Monitors', loc='right', fontsize=18)
            a.tick_params(labelsize=15)
            a.grid(True)

            ax[0].legend(fontsize=12, loc=1)
            ax[1].legend(fontsize=12, loc=4)

        # ax[0].set_ylim([-29.9999, 30])
        # ax[1].set_ylim([-30,    29.9999])

        ax[0].set_title(title, loc='right', fontsize=18)

        if draw_txt and container is not None:
            self.draw_text_lifetime(ax[0], container, text_pos)


    def draw_text_lifetime(self, ax, container, pos=None):
        '''
        Draw info text on plot
        '''
        date = datetime.datetime.strptime(str(container['date']), '%Y%m%d-%H%M%S')

        short_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

        textstr = '\n'.join((
            r'Run %i' % (container['run'], ),
            r'%s' % (date.strftime("%B %d, %Y - %H:%M"), ),
            r'Cathode HV = %.0f V' % (container['hv_cathode'], ),
            r'Anode Grid HV = %.0f V' % (container['hv_anodegrid'], ),
            r'Anode HV = %.0f V' % (container['hv_anode'], ),
            r'n traces = %.0i' % (len(container['ch_B']), ),
        ))

        if pos is None:
            pos = [0.98, 0.15]

        props = {"boxstyle": 'round', "edgecolor": 'grey', "facecolor": 'white', "alpha": 0.8,}
        ax.text(pos[0], pos[1], textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='bottom',
                horizontalalignment='left',
                bbox=props)

        props = {"boxstyle": 'round', "edgecolor": 'white', "facecolor": 'white', "alpha": 0,}
        ax.text(0.6, 1, 'SBNDPurityMonitorDAQ: ' + short_hash, transform=ax.transAxes, fontsize=8,
                verticalalignment='bottom',
                horizontalalignment='right',
                bbox=props)
