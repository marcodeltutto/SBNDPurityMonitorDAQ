'''
Contains PrM analysis fitter classes
'''

import datetime
import subprocess
import functools

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import scipy.optimize

from .analysis_base import PrMAnalysisBase

#pylint: disable=invalid-name,too-many-instance-attributes,too-many-arguments,consider-using-f-string,invalid-unary-operand-type,too-many-return-statements,bare-except,multiple-statements,dangerous-default-value,too-many-lines,broad-exception-caught,arguments-differ
class PrMAnalysisFitter(PrMAnalysisBase):
    '''
    A class to perform PrM analysis by fitting waveforms, See arXiv:2005.08187 for details.
    '''
    def __init__(
        self,
        wf_c, wf_a,
        samples_per_sec=2e6, config={}, wf_c_hvoff=None, wf_a_hvoff=None, debug=True
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
        super().__init__(
            wf_c, wf_a,
            samples_per_sec=samples_per_sec,
            config=config,
            wf_c_hvoff=wf_c_hvoff,
            wf_a_hvoff=wf_a_hvoff,
            debug=debug
        )

        self._samples_per_sec = samples_per_sec

        self._wf_x = self._raw_wf_x

        self._baseline_c_pre = None
        self._baseline_c_pre_err = None
        self._baseline_c_post = None
        self._baseline_c_post_err = None
        self._baseline_a_pre = None
        self._baseline_a_pre_err = None
        self._baseline_a_post = None
        self._baseline_a_post_err = None

        self._t_start_c = None
        self._t_start_c_err = None
        self._t_rise_c = None
        self._t_rise_c_err = None
        self._t_start_a = None
        self._t_start_a_err = None
        self._t_rise_a = None
        self._t_rise_a_err = None

        self._t_c_cgrid = None
        self._t_c_cgrid_err = None
        self._t_cgrid_agrid = None
        self._t_cgrid_agrid_err = None
        self._t_agrid_a = None
        self._t_agrid_a_err = None

        self._qa_err = None
        self._qc_err = None

        self._td_err = None
        self._tau_err = None

        self._fit_tau = np.inf # turn off lifetime effect in intial waveform fit

        self._lowpass_cutoff_freq = config.get('lowpass_cutoff_freq', 100e3)
        self._a_fit_start_offset = config.get('anode_fit_start_offset', 500)
        self._fit_iterations = config.get('lifetime_factor_fit_iterations', 10)

    def calculate(self):
        '''
        Performs all the calculation
        '''
        self._err = self._pre_process(self._lowpass_cutoff_freq)
        if self._err != 'ok':
            self._process_error(self._err)
            return

        # Perform fit iteratively, updating the lifetime parameter each time.
        # This way we account for effect of lifetime during drift between anode/cathode and grids.
        for i in range(self._fit_iterations):
            self._err = self._fit_cathode()
            if self._err != 'ok':
                self._process_error(self._err)
                return

            self._err = self._fit_anode()
            if self._err != 'ok':
                self._process_error(self._err)
                return

            self._err = self._calculate_delta_ts()
            if self._err != 'ok':
                self._process_error(self._err)
                return

            self._err = self._calculate_lifetime()
            if self._err != 'ok':
                self._process_error(self._err)
                return

            if i + 1 != self._fit_iterations:
                self._fit_tau = self._tau

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

        ax[0].plot(
            self._raw_wf_x, self._raw_wf_a, label='Anode Raw', color=_colors[0], alpha=0.5
        )
        ax[1].plot(
            self._raw_wf_x, self._raw_wf_c, label='Cathode Raw', color=_colors[1], alpha=0.5
        )
        ax[0].plot(self._wf_x, self._wf_a, label='Anode', color=_colors[0])
        ax[1].plot(self._wf_x, self._wf_c, label='Cathode', color=_colors[1])

        ax[0].plot(
            self._wf_x,
            self._fit_func(
                self._fit_tau,
                self._wf_x,
                self._baseline_a_pre, self._baseline_a_post,
                self._qa,
                self._t_start_a, self._t_rise_a
            ),
            label='Anode Fit',
            c='k'
        )
        ax[1].plot(
            self._wf_x,
            self._fit_func(
                self._fit_tau,
                self._wf_x,
                self._baseline_c_pre, self._baseline_c_post,
                -self._qc,
                self._t_start_c, self._t_rise_c
            ),
            label='Cathode Fit',
            c='k'
        )

        ax[0].axvline(self._t_start_c, color='grey', linestyle='dashed')
        ax[1].axvline(self._t_start_c, color='grey', linestyle='dashed')
        ax[0].axvline(self._t_rise_a, color='grey', linestyle='dashed')
        ax[1].axvline(self._t_rise_a, color='grey', linestyle='dashed')

        ax[0].axvspan(self._t_start_a, self._t_rise_a, alpha=0.5, color=_colors[0])
        ax[1].axvspan(self._t_start_c, self._t_rise_c, alpha=0.5, color=_colors[1])

        x_plot_range = self._t_rise_a * 2
        ax[0].set_xlim([0, x_plot_range])
        ax[1].set_xlim([0, x_plot_range])

        y_plot_range = np.abs(self._qc) * 1.4
        ax[0].set_ylim([-29.99, y_plot_range])
        ax[1].set_ylim([-y_plot_range, 29.99])

        ax[0].set_title(
            (
                f'Drift time: {self._td/1e3:.2f} ' + r'$ms$'
                f'\nQa/Qc: {self._qa/self._qc:.2f}'
                f'\nLifetime: {self._tau/1e3:.2f} ' + r'$ms$'
            ),
            loc='left',
            fontsize=12
        )

        self._set_lifetime_axis(ax, self._plot_title, container, text_pos=[0.015, 0.56])

        if savename:
            plt.savefig(savename)
        plt.show()

        return fig, ax

    def _pre_process(self, cutoff_freq):
        '''
        Applies a low-pass filter to the raw waveform

        Args:
            cutoff_freq (float): cut-off frequency for low-pass filter
        '''
        nyquist_freq = self._samples_per_sec / 2
        crit_freq = cutoff_freq / nyquist_freq # normalise the cut-off
        b, a = scipy.signal.butter(3, crit_freq)
        self._wf_c = scipy.signal.filtfilt(b, a, self._raw_wf_c)
        self._wf_a = scipy.signal.filtfilt(b, a, self._raw_wf_a)

        return 'ok'

    def _fit_func(self, tau, t, baseline_pre, baseline_post, V_0, t_start, t_rise):
        '''
        Fit function for PrM waveforms. Applied to cathode and anode signal separately.
        Two baselines are useful since baseline can sometimes change after discharge.
        tau should be fixed with functools.partial before fitting.

        Args:
            tau (float): fixed parameter, lifetime
            t (float): time variable
            baseline_pre (float): fit parameter
            baseline_post (float): fit parameter
            V_0 (float): fit parameter
            t_start (float): fit parameter
            t_rise (float): fit parameter
        '''
        return np.piecewise(
            t,
            [
                t < t_start, # before electrons freed at cathode or before arriving at anode grid
                (t >= t_start) & (t < t_rise), # drifting to cathode grid or anode
                t >= t_rise # past cathode grid or collected at anode
            ],
            [
                lambda t: (
                    baseline_pre
                ),
                lambda t: (
                    V_0 * (np.exp(-(t - t_start) / self._RC) - np.exp(-(t - t_start) / tau)) / ((t_rise - t_start) / (tau**(-1) -  self._RC**(-1))**(-1)) + # charging
                    baseline_pre
                ),
                lambda t: (
                    (
                        (V_0 * (np.exp(-(t_rise - t_start) / self._RC) - np.exp(-(t_rise - t_start) / tau)) / ((t_rise - t_start) / (tau**(-1) -  self._RC**(-1))**(-1))) +  # V max
                        (baseline_pre - baseline_post) # smoothly go to new baseline
                    ) *
                    np.exp(-(t - t_rise) / self._RC) + # discharging from V max
                    baseline_post
                )
            ]
        )

    def _fit_cathode(self):
        '''
        Apply fitting function to cathode.
        '''
        fit_func = functools.partial(self._fit_func, self._fit_tau)

        cathode_p_guess = [
            np.mean(self._wf_c[self._baseline_range_c[0]:self._baseline_range_c[1]]), # baseline_pre
            np.mean(self._wf_c[self._baseline_range_c[0]:self._baseline_range_c[1]]), # baseline_post
            np.min(self._wf_c), # V_0
            self._wf_x[np.argmin(self._wf_c) - 100], # t_start
            self._wf_x[np.argmin(self._wf_c)] # t_rise
        ]

        try:
            popt_cathode, pcov_cathode = scipy.optimize.curve_fit(
                fit_func, self._wf_x, self._wf_c,
                p0=cathode_p_guess,
                bounds=(
                    [-np.inf, -np.inf, -np.inf, 0.0, 0.0],
                    [np.inf, np.inf, 0.0, max(self._wf_x), max(self._wf_x)]
                )
            )
        except Exception as e:
            print(e)
            return 'fit_failed'

        self._baseline_c_pre, self._baseline_c_post, self._qc, self._t_start_c, self._t_rise_c = (
            popt_cathode
        )
        self._qc = -self._qc
        _, _, self._qc_err, self._t_start_c_err, self._t_rise_c_err = (
            np.sqrt(np.diag(pcov_cathode))
        )

        if self._debug:
            print(np.column_stack([
                ['baseline_c_pre', 'baseline_c_post', 'qc', 't_start_c', 't_rise_c'],
                popt_cathode,
                np.sqrt(np.diag(pcov_cathode))
            ]))

        return 'ok'

    def _fit_anode(self):
        '''
        Apply fitting function to anode.
        '''
        fit_func = functools.partial(self._fit_func, self._fit_tau)

        anode_max_tick = np.argmax(self._wf_a)
        anode_p_guess = [
            np.mean(self._wf_a[self._baseline_range_a[0]:self._baseline_range_a[1]]), # baseline
            np.mean(self._wf_a[self._baseline_range_a[0]:self._baseline_range_a[1]]), # baseline
            np.max(self._wf_a), # V_0
            self._wf_x[anode_max_tick - 100], # t_start
            self._wf_x[anode_max_tick] # t_rise
        ]

        try:
            popt_anode, pcov_anode = scipy.optimize.curve_fit(
                fit_func,
                self._wf_x[anode_max_tick - self._a_fit_start_offset:],
                self._wf_a[anode_max_tick - self._a_fit_start_offset:],
                p0=anode_p_guess,
                bounds=(
                    [-np.inf, -np.inf, 0.0, 0.0, 0.0],
                    [np.inf, np.inf, np.inf, max(self._wf_x), max(self._wf_x)]
                )
            )
        except Exception as e:
            print(e)
            return 'fit_failed'

        self._baseline_a_pre, self._baseline_a_post, self._qa, self._t_start_a, self._t_rise_a = (
            popt_anode
        )
        _, _, self._qa_err, self._t_start_a_err, self._t_rise_a_err = (
            np.sqrt(np.diag(pcov_anode))
        )

        if self._debug:
            print(np.column_stack([
                ['baseline_a_pre', 'baseline_a_post', 'qa', 't_start_a', 't_rise_a'],
                popt_anode,
                np.sqrt(np.diag(pcov_anode))
            ]))

        return 'ok'

    def _calculate_delta_ts(self):
        '''
        Calculate and check time differences needed for lifetime calculation
        '''
        self._t_c_cgrid = self._t_rise_c - self._t_start_c
        self._t_c_cgrid_err = np.sqrt(self._t_rise_c_err**2 + self._t_start_c_err**2)

        self._t_cgrid_agrid = self._t_start_a - self._t_rise_c
        self._t_cgrid_agrid_err = np.sqrt(self._t_start_a_err**2 + self._t_rise_c_err**2)

        self._t_agrid_a = self._t_rise_a - self._t_start_a
        self._t_agrid_a_err = np.sqrt(self._t_rise_a_err**2 + self._t_start_a_err**2)

        if self._t_c_cgrid < 0 or self._t_cgrid_agrid < 0 or self._t_agrid_a < 0:
            return 'deltat_negative'

        if self._debug:
            print(np.column_stack([
                ['t_c_cgrid', 't_cgrid_agrid', 't_agrid_a'],
                [self._t_c_cgrid, self._t_cgrid_agrid, self._t_agrid_a],
                [self._t_c_cgrid_err, self._t_cgrid_agrid_err, self._t_agrid_a_err],
            ]))

        return 'ok'

    def _calculate_lifetime(self):
        '''
        Lifetime calculation.
        '''
        R = self._qa / self._qc
        R_err = R * np.sqrt((self._qa_err / self._qa)**2 + (self._qc_err / self._qc)**2)

        self._tau = (-1 / np.log(R)) * (self._t_cgrid_agrid + (self._t_c_cgrid + self._t_agrid_a) / 2)
        self._tau_err = (
            self._tau * np.sqrt(
                ((1 / np.log(R)) * (R_err / R))**2 +
                (
                    np.sqrt(
                        self._t_cgrid_agrid_err**2 +
                        (self._t_c_cgrid_err / 2)**2 +
                        (self._t_agrid_a_err / 2)**2
                    ) /
                    (self._t_cgrid_agrid + (self._t_c_cgrid + self._t_agrid_a) / 2)
                )**2
            )
        )

        # Just for consistency, not used in the lifetime calculation
        self._td = self._t_rise_a - self._t_start_c
        self._td_err = np.sqrt(self._t_rise_a_err**2 + self._t_start_c_err**2)

        if self._debug:
            print(np.column_stack([
                ['R', 'tau', 'td'], [R, self._tau, self._td], [R, self._tau_err, self._td_err]
            ]))

        return 'ok'

    def _set_lifetime_axis(self, ax, title, container=None, draw_txt=True, text_pos=None):
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
            self._draw_text_lifetime(ax[0], container, text_pos)

    def _draw_text_lifetime(self, ax, container, pos=None):
        '''
        Draw info text on plot
        '''
        date = container["date"]
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


class PrMAnalysisFitterDiff(PrMAnalysisFitter):
    '''
    A class to perform PrM analysis by fitting the difference of the cathode and anode waveforms.
    The same as PrMAnalysisFitter with the fitting functions summed
    '''
    def __init__(
        self,
        wf_c, wf_a,
        samples_per_sec=2e6, config={}, wf_c_hvoff=None, wf_a_hvoff=None, debug=True
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
        super().__init__(
            wf_c, wf_a,
            samples_per_sec=samples_per_sec,
            config=config,
            wf_c_hvoff=wf_c_hvoff,
            wf_a_hvoff=wf_a_hvoff,
            debug=debug
        )

        self._raw_wf_diff = self._raw_wf_c - self._raw_wf_a
        self._wf_diff = None

    def calculate(self):
        '''
        Performs all the calculation
        '''
        self._err = self._pre_process(self._lowpass_cutoff_freq)
        if self._err != 'ok':
            self._process_error(self._err)
            return

        # Perform fit iteratively, updating the lifetime parameter each time.
        # This way we account for effect of lifetime during drift between anode/cathode and grids.
        for i in range(self._fit_iterations):
            self._err = self._fit_diff()
            if self._err != 'ok':
                self._process_error(self._err)
                return

            self._err = self._calculate_delta_ts()
            if self._err != 'ok':
                self._process_error(self._err)
                return

            self._err = self._calculate_lifetime()
            if self._err != 'ok':
                self._process_error(self._err)
                return

            if i + 1 != self._fit_iterations:
                self._fit_tau = self._tau

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
        _color = prop_cycle.by_key()['color'][0]

        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(12, 8), sharex=True)
        fig.subplots_adjust(hspace=0)

        ax.plot(
            self._raw_wf_x, self._raw_wf_diff, label='Cathode - Anode Raw', color=_color, alpha=0.5
        )
        ax.plot(self._wf_x, self._wf_diff, label='Cathode - Anode', color=_color)

        ax.plot(
            self._wf_x,
            self._fit_func(
                self._fit_tau,
                self._wf_x,
                self._baseline_c_pre, self._baseline_c_post,
                -self._qc,
                self._t_start_c, self._t_rise_c,
                self._baseline_a_pre, self._baseline_a_post,
                self._qa,
                self._t_start_a, self._t_rise_a
            ),
            label='Cathode - Anode Fit',
            c='k'
        )

        ax.axvline(self._t_start_c, color='grey', linestyle='dashed')
        ax.axvline(self._t_start_c, color='grey', linestyle='dashed')
        ax.axvline(self._t_rise_a, color='grey', linestyle='dashed')
        ax.axvline(self._t_rise_a, color='grey', linestyle='dashed')

        ax.axvspan(self._t_start_a, self._t_rise_a, alpha=0.5, color=_color)
        ax.axvspan(self._t_start_c, self._t_rise_c, alpha=0.5, color=_color)

        x_plot_range = self._t_rise_a * 2
        ax.set_xlim([0, x_plot_range])

        y_plot_range = np.abs(self._qc) * 1.4
        ax.set_ylim([-y_plot_range, 29.99])

        ax.set_title(
            (
                f'Drift time: {self._td/1e3:.2f} ' + r'$ms$'
                f'\nQa/Qc: {self._qa/self._qc:.2f}'
                f'\nLifetime: {self._tau/1e3:.2f} ' + r'$ms$'
            ),
            loc='left',
            fontsize=12
        )

        self._set_lifetime_axis(ax, self._plot_title, container, text_pos=[0.015, 0.76])

        if savename:
            plt.savefig(savename)
        plt.show()

        return fig, ax

    def _pre_process(self, cutoff_freq):
        '''
        Applies a low-pass filter to the raw waveform

        Args:
            cutoff_freq (float): cut-off frequency for low-pass filter
        '''
        nyquist_freq = self._samples_per_sec / 2
        crit_freq = cutoff_freq / nyquist_freq # normalise the cut-off
        b, a = scipy.signal.butter(3, crit_freq)
        self._wf_diff = scipy.signal.filtfilt(b, a, self._raw_wf_diff)
        # Still useful to have these for making initial fitting guesses
        self._wf_c = scipy.signal.filtfilt(b, a, self._raw_wf_c)
        self._wf_a = scipy.signal.filtfilt(b, a, self._raw_wf_a)

        return 'ok'

    def _fit_func(
        self,
        tau,
        t,
        baseline_c_pre, baseline_c_post, V_0_c, t_start_c, t_rise_c,
        baseline_a_pre, baseline_a_post, V_0_a, t_start_a, t_rise_a
    ):
        '''
        Fit function for cathode - anode PrM waveforms.
        Multiple baselines are useful since baseline can sometimes change after discharge.

        Args:
            tau (float): fixed parameter, lifetime
            t (float): time variable
            baseline_c_pre (float): parameter
            baseline_c_post (float): parameter
            V_0_c (float): parameter
            t_start_c (float): parameter
            t_rise_c (float): parameter
            baseline_a_pre (float): parameter
            baseline_a_post (float): parameter
            V_0_a (float): parameter
            t_start_a (float): parameter
            t_rise_a (float): parameter
        '''
        return np.piecewise(
            t,
            [
                t < t_start_c, # before electrons feed
                (t >= t_start_c) & (t < t_rise_c), # drifting to cathode grid
                (t >= t_rise_c) & (t < t_start_a), # drifting to anode grid
                (t >= t_start_a) & (t < t_rise_a), # drifting to anode
                t >= t_rise_a # after electrons collected at anode
            ],
            [
                lambda t: (
                    baseline_c_pre - baseline_a_pre
                ),
                lambda t: (
                    V_0_c * (np.exp(-(t - t_start_c) / self._RC) - np.exp(-(t - t_start_c) / tau)) / ((t_rise_c - t_start_c) / (tau**(-1) -  self._RC**(-1))**(-1)) + # charging at cathode
                    baseline_c_pre - baseline_a_pre
                ),
                lambda t: (
                    (
                        (V_0_c * (np.exp(-(t_rise_c - t_start_c) / self._RC) - np.exp(-(t_rise_c - t_start_c) / tau)) / ((t_rise_c - t_start_c) / (tau**(-1) -  self._RC**(-1))**(-1))) + # V_max
                        (baseline_c_pre - baseline_c_post) # Smooth baseline change
                    ) *
                    np.exp(-(t - t_rise_c) / self._RC) + # discharging at cathode
                    baseline_c_post - baseline_a_pre
                ),
                lambda t: (
                    (
                        (V_0_c * (np.exp(-(t_rise_c - t_start_c) / self._RC) - np.exp(-(t_rise_c - t_start_c) / tau)) / ((t_rise_c - t_start_c) / (tau**(-1) -  self._RC**(-1))**(-1))) +
                        (baseline_c_pre - baseline_c_post)
                    ) *
                    np.exp(-(t - t_rise_c) / self._RC) - # discharging at cathode
                    V_0_a * (np.exp(-(t - t_start_a) / self._RC) - np.exp(-(t - t_start_a) / tau)) / ((t_rise_a - t_start_a) / (tau**(-1) -  self._RC**(-1))**(-1)) + # charging at anode
                    baseline_c_post - baseline_a_pre
                ),
                lambda t: (
                    (
                        (V_0_c * (np.exp(-(t_rise_c - t_start_c) / self._RC) - np.exp(-(t_rise_c - t_start_c) / tau)) / ((t_rise_c - t_start_c) / (tau**(-1) -  self._RC**(-1))**(-1))) +
                        (baseline_c_pre - baseline_c_post)
                    ) *
                    np.exp(-(t - t_rise_c) / self._RC) - # discharging at cathode
                    (
                        V_0_a * (np.exp(-(t_rise_a - t_start_a) / self._RC) - np.exp(-(t_rise_a - t_start_a) / tau)) / ((t_rise_a - t_start_a) / (tau**(-1) -  self._RC**(-1))**(-1)) + # V_max
                        (baseline_a_pre - baseline_a_post) # smooth baseline change
                    ) *
                    np.exp(-(t - t_rise_a) / self._RC) + # discharging at anode
                    baseline_c_post - baseline_a_post
                )
            ]
        )

    def _fit_diff(self):
        '''
        Apply fitting function to cathode - anode waveform.
        '''
        fit_func = functools.partial(self._fit_func, self._fit_tau)

        anode_max_tick = np.argmax(self._wf_a)
        p_guess = [
            np.mean(self._wf_c[self._baseline_range_c[0]:self._baseline_range_c[1]]), # baseline_c_pre
            np.mean(self._wf_c[self._baseline_range_c[0]:self._baseline_range_c[1]]), # baseline_c_post
            np.min(self._wf_c), # V_0_c
            self._wf_x[np.argmin(self._wf_c) - 100], # t_start_c
            self._wf_x[np.argmin(self._wf_c)], # t_rise_c
            np.mean(self._wf_a[self._baseline_range_a[0]:self._baseline_range_a[1]]), # baseline_c_pre
            np.mean(self._wf_a[self._baseline_range_a[0]:self._baseline_range_a[1]]), # baseline_c_post
            np.max(self._wf_a), # V_0_c
            self._wf_x[anode_max_tick - 100], # t_start_c
            self._wf_x[anode_max_tick] # t_rise_c
        ]

        try:
            popt, pcov = scipy.optimize.curve_fit(
                fit_func, self._wf_x, self._wf_diff,
                p0=p_guess,
                bounds=(

                    [-np.inf, -np.inf, -np.inf, 0.0, 0.0, -np.inf, -np.inf, 0.0, 0.0, 0.0],
                    [np.inf, np.inf, 0.0, max(self._wf_x), max(self._wf_x), np.inf, np.inf, np.inf, max(self._wf_x), max(self._wf_x)]
                )
            )
        except Exception as e:
            print(e)
            return 'fit_failed'

        (
            self._baseline_c_pre,
            self._baseline_c_post,
            self._qc,
            self._t_start_c,
            self._t_rise_c,
            self._baseline_a_pre,
            self._baseline_a_post,
            self._qa,
            self._t_start_a,
            self._t_rise_a
        ) = popt
        self._qc = -self._qc
        (
            _,
            _,
            self._qc_err,
            self._t_start_c_err,
            self._t_rise_c_err,
            _,
            _,
            self._qa_err,
            self._t_start_a_err,
            self._t_rise_a_err
        ) = np.sqrt(np.diag(pcov))

        if self._debug:
            print(np.column_stack([
                [
                    'baseline_c_pre', 'baseline_c_post', 'qc', 't_start_c', 't_rise_c',
                    'baseline_a_pre', 'baseline_a_post', 'qa', 't_start_a', 't_rise_a'
                ],
                popt,
                np.sqrt(np.diag(pcov))
            ]))

        return 'ok'

    def _set_lifetime_axis(self, ax, title, container=None, draw_txt=True, text_pos=None):
        '''
        Customizes the axis
        '''
        ax.set_ylabel('Waveform [mV]',fontsize=18)
        ax.set_xlabel('Time [us]',fontsize=18)
        ax.tick_params(labelsize=15)
        ax.grid(True)

        ax.legend(fontsize=12, loc=1)

        ax.set_title(title, loc='right', fontsize=18)

        if draw_txt and container is not None:
            self._draw_text_lifetime(ax, container, text_pos)
