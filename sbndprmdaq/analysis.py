'''
Contains PrM analysis class
'''

import datetime
import numpy as np
import subprocess


class PrMAnalysis:
    '''
    A class to perform quick PrM analysis
    '''

    _deltat_start_c = 450
    _deltat_start_a = 900
    _trigger_sample = 512 # When the flash lamp flashes

    def __init__(self, wf_c, wf_a, samples_per_sec=2e6):
        '''
        Constructor.

        Args:
            wf_c (list): cathode waveforms
            wf_a (list): anode waveforms
        '''
        volt_to_mv = 1e3
        sec_to_us = 1e6

        self._raw_wf_x = np.arange(len(wf_c[0])) / samples_per_sec * sec_to_us # us
        self._raw_wf_c = np.mean(wf_c, axis=0) * volt_to_mv
        self._raw_wf_a = np.mean(wf_a, axis=0) * volt_to_mv

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
            print(len(self._raw_wf_x), '->', len(self._wf_x))
        else:
            self._wf_c = self._raw_wf_c
            self._wf_a = self._raw_wf_a
            self._wf_x = self._raw_wf_x

    def estimate_baseline(self, baseline_range_c=[0,450],  baseline_range_a=[1000,2000]):
        '''
        Baseline estimation

        Args:
            baseline_range_c (list): Range used to estimate baseline for cathode
            baseline_range_a (list): Range used to estimate baseline for anode
        '''
        self._baseline_c = np.mean(self._wf_c[baseline_range_c])
        self._baseline_rms_c = np.std(self._wf_c[baseline_range_c])

        self._baseline_a = np.mean(self._wf_a[baseline_range_a])
        self._baseline_rms_a = np.std(self._wf_a[baseline_range_a])


    def estimate_deltat(self):
        '''
        Delta t estimation
        '''

        # _trigger_sample += self._offset
        # _deltat_start_c -= self._offset
        # _deltat_start_a -= self._offset
        
        # Cathode
        tmp_wvf = self._wf_c[self._deltat_start_c:]
        min_idx = np.argmin(tmp_wvf)
        print('min_idx', min_idx)
        selected = tmp_wvf[0:min_idx]
        # print('->', selected, np.argwhere((selected-(base-base_rms))>0))
        if self._trigger_sample:
            start_idx = self._trigger_sample - self._deltat_start_c
        else:
            start_idx = np.argwhere((selected-(self._baseline_c-self._baseline_rms_c))>0)[-1]
        start = self._wf_x[start_idx + self._deltat_start_c]
        end = self._wf_x[min_idx + self._deltat_start_c]
        print('Cathode: start', start, 'end', end)
        self._time_start_c = start
        self._time_end_c = end
        self._deltat_c = end - start

        # Anode
        tmp_wvf = self._wf_a[self._deltat_start_a:]
        max_idx = np.argmax(tmp_wvf)
        selected = tmp_wvf[0:max_idx]

        # FInd start of anode wf (when is 10% from the baseline)
        th = (selected[-1] - self._baseline_a) * 0.1
        start_idx = np.argwhere((selected-self._baseline_a)<th)[-1]
        start = self._wf_x[start_idx + self._deltat_start_a]
        end = self._wf_x[max_idx + self._deltat_start_a]
        print('Anode: start', start, 'end', end)
        self._time_start_a = start[0]
        self._time_end_a = end
        self._deltat_a = end - start[0]

    def rc_correction(self, delta_t, RC=119):
        '''
        RC correction estimation

        Args:
            delta_t (float): rise time
            RC (float): RC time constant
        '''
        return (delta_t / RC) * (1 / (1 - np.exp(-delta_t/RC)))

    def calculate_lifetime(self, start_idx=550):
        '''
        Lifetime estimation

        Args:
            start_idx (int): where to start estimation (to esclude lamp noise) 
        '''

        self._max_c = np.min(self._wf_c[start_idx:])
        self._max_a = np.max(self._wf_a[start_idx:])

        # self._max_c += self._baseline_rms_c
        # self._max_a -= self._baseline_rms_a

        rc_correction_c = self.rc_correction(self._deltat_c, RC=119)
        rc_correction_a = self.rc_correction(self._deltat_a, RC=119)

        print('RC correction: C', rc_correction_c, ', A', rc_correction_a)

        self._qc = (self._max_c - self._baseline_c) * rc_correction_c
        self._qa = (self._max_a - self._baseline_a) * rc_correction_a

        self._qc = np.abs(self._qc)
        print(type(self._max_a), type(self._baseline_a), type(rc_correction_a), type(self._qa))

        print('Qc', self._qc, ', QA', self._qa, 'Qa/Qc', self._qa/self._qc)
        
        self._td = self._time_end_a - self._time_start_c
        
        print('Drift time', self._td)
        
        self._tau = -self._td/np.log(self._qa/self._qc)

        print('Lifetime', self._tau)
        
        

    def calculate(self):
        '''
        Performs all the calculation
        '''

        self.pre_process(smooth=True, n=40)

        self.estimate_baseline()

        self.estimate_deltat()

        self.calculate_lifetime()

    def plot_summary(self, container=None, savename=None):
        '''
        Generates a summary plot

        Args:
            container (dict): data container to add info on plot
            savename (string): full path to save file
        '''

        import matplotlib.pyplot as plt
        # import matplotlib.patches as patches

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
        
        ax[0].set_ylim([-29.9999, 50])
        ax[1].set_ylim([-50, 29.9999])
                
        ax[0].set_title(f'Drift time: {self._td/1e3:.2f} ' + r'$ms$'
                        + f'\nQa/Qc: {self._qa/self._qc:.2f}'
                        + f'\nLifetime: {self._tau/1e3:.2f} ' + r'$ms$',
                        loc='left', fontsize=12)
        
        self.set_lifetime_axis(ax, 'SBND PrM 3 - Inline - Long', container, text_pos=[0.27, 0.56])

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

        props = dict(boxstyle='round', edgecolor='grey', facecolor='white', alpha=0.8)        
        ax.text(pos[0], pos[1], textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='bottom',
                horizontalalignment='left',
                bbox=props)

        props = dict(boxstyle='round', edgecolor='white', facecolor='white', alpha=0)
        ax.text(0.6, 1, 'SBNDPurityMonitorDAQ: ' + short_hash, transform=ax.transAxes, fontsize=8,
                verticalalignment='bottom',
                horizontalalignment='right',
                bbox=props)
