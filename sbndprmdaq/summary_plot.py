'''
Contains class to make summary purity plots
'''

import logging
import time
import datetime
import xml.etree.ElementTree as ET
import requests

from PyQt5.QtCore import QTimer

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from labellines import labelLine, labelLines
import numpy as np

from sbndprmdaq.eclapi import ECL, ECLEntry


class SummaryPlot:
    '''
    A class that makes a plot of electron lifetime versus time, using teh measurement made
    by the purity monitor DAQ and stored in a CSV file (dataframe).
    '''
    #pylint: disable=invalid-name,too-many-locals

    def __init__(self, config):
        '''
        Contructor.

        Args:
            config (dict): the configuration
        '''

        self._timer = None
        # self._timer_single = None

        self._dataframe_filename = None
        self._plot_savedir = None

        self._first_day = {
            1: "03/24/2024",
            2: "02/20/2024",
            3: "02/20/2024",
        }

        self._config = config['summary_plot']

        self._logger = logging.getLogger(__name__)

        self._current_plots = {}

        self._n_runs = {}

        if self._config['make_summary_plots']:

            seconds_to_start = self.seconds_until_hour(self._config['start_hour'])
            seconds_to_start = 20
            # self._timer_single = QTimer.singleShot(seconds_to_start * 1000, self.start_periodic_plotting)

            self._timer = QTimer()
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self.start_periodic_plotting)
            self._timer.start(seconds_to_start * 1000)

            self._logger.info(f'The first summary plot will be made in {seconds_to_start/3600:.2f} hours.')


    def start_periodic_plotting(self):
        '''
        Starts the timer to make periodic plots
        '''

        self._logger.info('Making the first summary plot.')

        self.make_summary_plots()

        self._timer = QTimer()
        self._timer.timeout.connect(self.make_summary_plots)
        self._timer.start(self._config['time_interval'] * 1000 * 3600)


    def set_dataframe_path(self, dataframe_filename):
        '''
        Sets the path to the CSV file containing the dataframe
        '''

        self._dataframe_filename = dataframe_filename


    def set_plot_savedir(self, plot_savedir):
        '''
        Sets the path to the directory where to save the plots
        '''

        self._plot_savedir = plot_savedir


    def make_summary_plots(self):
        '''
        Makes the plots for all PrMs
        '''

        if self._dataframe_filename is None:
            self._logger.warning('Dont have a dataframe filename. Plot will not be made.')
            return

        # Read the dataframe
        df = pd.read_csv(self._dataframe_filename)

        # Add Qa/Qc ratio
        df['qaqc'] = df['qa']/df['qc']

        # Convert the date string to datetime object
        df['date'] = pd.to_datetime(df['date'])

        # Add a datetime index
        df['datetime'] = pd.to_datetime(df['date'])
        df = df.set_index('datetime')

        # Drop old column
        df = df.drop(['Unnamed: 0'], axis=1)


        self._make_summary_plot(df)

        self._number_of_runs(df, prm_ids=[1, 2, 3])

        self._send_to_ecl()


    def _make_summary_plot(self, df):
        '''
        Makes the plot for a single PrM

        Args:
            df (dataframe): The dataframe with the measurements
        '''

        labels = {
            1: 'PrM 1, Internal, Long',
            2: 'PrM 2, Internal, Short',
            3: 'PrM 3, Inline, Long',
        }

        linestyles = [
            'solid',
            'dashed',
            'dashdot',
            'dotted',
            (0, (1, 10)),
            (5, (10, 3)),
            (10, (5, 10)),
        ]

        dfs = {}

        for prm_id in self._config['prms']:

            # Select entries past a certain day
            first_day = datetime.datetime.strptime(self._first_day[prm_id], "%m/%d/%Y")
            mask = df['date'] > first_day
            df_s = df[mask]

            dfs[prm_id] = df_s.query(f'prm_id == {prm_id} and qaqc > 0 and qaqc < 1')

        timestr = time.strftime("%Y%m%d-%H%M%S")

        self._current_plots = {}

        events = {
            datetime.datetime(2024, 3, 25, 15, 00): 'Lowered HV on PrM 2',
            datetime.datetime(2024, 5, 26, 8, 50): 'Increased HV on PrM 2',
        }

        #
        # Lifetime Plot
        #

        _, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 8))

        for prm_id in self._config['prms']:
            ax.plot(dfs[prm_id]['date'], dfs[prm_id]['lifetime'], label=labels[prm_id], linestyle='None', marker="o", markersize=3)

        for i, (day, label) in enumerate(events.items()):
            ax.axvline(day, color='gray', label=label, linestyle=linestyles[i])

        ax.set_ylabel(r'Lifetime [$ms$]',fontsize=16)
        ax.set_xlabel('Time',fontsize=16)
        ax.tick_params(labelsize=12)
        ax.grid(True)

        ax.set_title('Preliminary', loc='right', color='gray')
        ax.legend(fontsize=12, loc=2)

        ax.set_ylim([0.050, 8.0])

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        plt.tight_layout()

        if self._plot_savedir is not None:
            filename = self._plot_savedir + f'prm1_2_lifetime_{timestr}.png'
            plt.savefig(filename)
            self._logger.info(f'Plot saved to {filename}.')
            self._current_plots['prm_lifetime'] = filename

        #
        # Qa and Qc Plot
        #
        for prm_id in self._config['prms']:
            _, ax = plt.subplots(ncols=2, nrows=1, figsize=(20, 8))

            ax[0].plot(dfs[prm_id]['date'], dfs[prm_id]['qc'], label=labels[prm_id],
                       linestyle='None', marker="o", markersize=5, color='blue', alpha=0.5)
            ax[1].plot(dfs[prm_id]['date'], dfs[prm_id]['qa'], label=labels[prm_id],
                       linestyle='None', marker="o", markersize=5, color='red', alpha=0.5)

            for i, (day, label) in enumerate(events.items()):
                if prm_id == 2:
                    ax[0].axvline(day, color='gray', label=label) #, linestyle=linestyles[i])
                    ax[1].axvline(day, color='gray', label=label) #, linestyle=linestyles[i])

            for a in ax:
                a.set_xlabel('Time',fontsize=16)
                a.tick_params(labelsize=12)
                a.grid(True)
                a.set_title('Preliminary', loc='right', color='gray')
                a.legend(fontsize=12, loc=3)
                plt.setp(a.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

            ax[0].set_ylabel(r'$Q_C$ [$mV$]',fontsize=16)
            ax[0].set_ylim([5, 33])

            ax[1].set_ylabel(r'$Q_A$ [$mV$]',fontsize=16)
            ax[1].set_ylim([0, 30])


            plt.tight_layout()

            if self._plot_savedir is not None:
                filename = self._plot_savedir + f'prm{prm_id}_qc_qa_{timestr}.png'
                plt.savefig(filename)
                self._logger.info(f'Plot saved to {filename}.')
                self._current_plots[f'prm{prm_id}_qcqa'] = filename

        #
        # Qa/Qc Plot
        #

        for prm_id in self._config['prms']:

            df_daily_mean = dfs[prm_id].resample('D').mean()
            df_daily_std = dfs[prm_id].resample('D').std()

            df_daily_mean['date'] = df_daily_mean.index
            df_daily_std['date'] = df_daily_std.index

            print(df_daily_mean)

            _, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 8))

            def qaqc(t, tau):
                return np.exp(-t/tau)

            date = np.array(dfs[prm_id]['date'])
            qa = np.array(dfs[prm_id]['qa'])
            qc = np.array(dfs[prm_id]['qc'])

            mask = (qa != -1) & (qc != -1)
                
            ax.plot(date[mask], qa[mask]/qc[mask], label=labels[prm_id],
                    linestyle='None', marker="o", markersize=5, color='green', alpha=0.5, zorder=1)

            ax.errorbar(df_daily_mean['date'], df_daily_mean['qaqc'], yerr=df_daily_std['qaqc'],
                        label=labels[prm_id] + ' Daily Average', linestyle='None', marker="o", markersize=5, color='black', alpha=1, zorder=2)


            ax.set_ylabel(r'$Q_A/Q_C$',fontsize=16)
            ax.set_xlabel('Time',fontsize=16)
            ax.tick_params(labelsize=12)
            ax.grid(True)
            ax.set_title('Preliminary', loc='right', color='gray')

            if prm_id == 1:
                for i, tau in enumerate([0.50, 1, 3, 6, 9]):
                    ax.axhline(qaqc(1.1, tau),
                               xmin=0,
                               xmax=1,
                               color='black', label=f'{tau:.2f} ms', linestyle=linestyles[i])
            else:
                d = datetime.datetime(2024, 3, 25, 15, 00)
                num = mpl.dates.date2num(d)
                xmin, xmax = ax.get_xlim()
                frac = (num - xmin) / (xmax - xmin)
                for i, tau in enumerate([0.10, 1, 3, 6, 9]):
                    ax.axhline(qaqc(0.25, tau),
                               xmin=0,
                               xmax=frac,
                               color='black', label=f'{tau:.2f} ms', linestyle=linestyles[i])
                
                    ax.axhline(qaqc(0.39, tau),
                               xmin=frac,
                               xmax=1,
                               color='black', linestyle=linestyles[i])

            ax.set_title('Preliminary', loc='right', color='gray')

            # labelLines(ax.get_lines())# , zorder=2.5)#, xvals=xvals)
            ax.legend(fontsize=12, loc=2)
            # for l in ax.get_lines():
            #     print('LINE:', l)
            ax.set_ylim([0, 1.1])

            plt.xticks(rotation=45, ha="right", rotation_mode="anchor")

            plt.tight_layout()
            if self._plot_savedir is not None:
                filename = self._plot_savedir + f'prm{prm_id}_qa_over_qc_{timestr}.png'
                plt.savefig(filename)
                self._logger.info(f'Plot saved to {filename}.')
                self._current_plots[f'prm{prm_id}_qa_over_qc'] = filename


        # plt.show()


    def _number_of_runs(self, df, prm_ids=(1, 2, 3)):

        password = self._read_ecl_password()

        # https://dbweb0.fnal.gov/ECL/sbnd
        ecl = ECL(url='https://dbweb9.fnal.gov:8443/ECL/sbnd/E', user='sbndprm', password=password)

        # Retrieve the last 20 entries
        text = ecl.search(limit=20)

        # Convert to XML
        xml = ET.fromstring(text)

        # Find the entry element in the XML tree
        entries = xml.findall('./entry')

        lasttime = None

        # Loop over entries (they are in decreasing order in time)
        for entry in entries:
            text = entry.find('./text').text

            if 'Purity Monitors Automated Plots' in text:

                timestr = entry.attrib['timestamp']
                lasttime = datetime.datetime.strptime(timestr, "%m/%d/%Y %H:%M:%S")
                break

        if lasttime is None:
            return

        self._logger.info(f'Found previous eLog automated entry from {lasttime}')

        for prm_id in prm_ids:

            df_sel = df.query(f'prm_id == {prm_id}')

            mask = df_sel['date'] > lasttime

            self._n_runs[prm_id] = len(df_sel[mask])

            self._logger.info(f'Number of runs for PrM {prm_id} since last automated eLog entry {self._n_runs[prm_id]}')



    def _send_to_ecl(self):

        if self._current_plots:

            password = self._read_ecl_password()

            ecl = ECL(url='https://dbweb9.fnal.gov:8443/ECL/sbnd/E', user='sbndprm', password=password)

            text=f'<font face="arial"> <b>Purity Monitors Automated Plots</b> <BR> {self._config["ecl_text"]}</font>'

            text = '<font face="arial"> '
            text += '<b>Purity Monitors Automated Plots</b> '
            text += '<BR> '
            text += f'{self._config["ecl_text"]} '
            text += '<BR> '
            text += 'Number of runs since last automated entry: '
            text += '<BR> '
            text += f'- PrM 1 (internal, long): {self._n_runs[1]}'
            text += '<BR> '
            text += f'- PrM 2 (internal, short): {self._n_runs[2]}'
            text += '<BR> '
            text += f'- PrM 3 (inline, long): {self._n_runs[3]}'
            text += '</font>'

            entry = ECLEntry(category='Purity Monitors', text=text, preformatted=True)

            for name, filename in self._current_plots.items():
                entry.add_image(name=name, filename=filename)

            print(entry.show())

            if self._config['post_to_ecl']:

                try:
                    ecl.post(entry, do_post=True)
                except:
                    self._logger.info('Post timeout. Trying one more time in 5 secs')
                    time.sleep(5)
                    ecl.post(entry, do_post=True)


    def _read_ecl_password(self):

        with open(self._config['ecl_pwd_file'], 'r', encoding="utf-8") as pwd_file:

            return pwd_file.readlines()[0].strip()


    def seconds_until_hour(self, target_hour):
        '''
        Returns the number of seconds until a certain hour is reached

        Args:
            target_hour (int): the hour of the day to reach (8 = 8 am, 20 = 8 pm)
        '''

        now = datetime.datetime.now()
        target_time = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)

        if now.hour < target_hour:
            # If the target hour is later in the day
            delta = target_time - now
        else:
            # If the target hour is tomorrow
            tomorrow = now + datetime.timedelta(days=1)
            target_time = tomorrow.replace(hour=target_hour, minute=0, second=0, microsecond=0)
            delta = target_time - now

        seconds = delta.total_seconds()
        return int(seconds)

    def remaining_time(self):
        '''
        Returns the remaining time on the timer to post summary plot on elog
        '''
        if self._timer is None:
            return None

        if self._timer.isActive():
            return self._timer.remainingTime()

        return None
