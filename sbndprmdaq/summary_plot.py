'''
Contains class to make summary purity plots
'''

import logging
import time
import datetime
import pandas as pd
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt

from sbndprmdaq.eclapi import ECL, ECLEntry

class SummaryPlot:
    '''
    A class that makes a plot of electron lifetime versus time, using teh measurement made
    by the purity monitor DAQ and stored in a CSV file (dataframe).
    '''
    #pylint: disable=invalid-name

    def __init__(self, config):
        '''
        Contructor.

        Args:
            config (dict): the configuration
        '''

        self._timer = None

        self._dataframe_filename = None
        self._plot_savedir = None

        self._first_day = "02/20/2024"

        self._config = config['summary_plot']

        self._logger = logging.getLogger(__name__)

        self._current_plots = {}

        if self._config['make_summary_plots']:

            seconds_to_start = self.seconds_until_hour(self._config['start_hour'])
            QTimer.singleShot(seconds_to_start * 1000, self.start_periodic_plotting)

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

        # Convert the date string to datetime object
        df['date'] = pd.to_datetime(df['date'])

        # Select entries past a certain day
        first_day = datetime.datetime.strptime(self._first_day, "%m/%d/%Y")
        mask = df['date'] > first_day
        df = df[mask]

        for prm_id in self._config['prms']:
            self._make_summary_plot(prm_id, df)

        if self._config['post_to_ecl']:
            self._send_to_ecl()


    def _make_summary_plot(self, prm_id, df):
        '''
        Makes the plot for a single PrM

        Args:
            prm_id (int): The purity monitor ID
            df (dataframe): The dataframe with the measurements
        '''

        label = ''
        if prm_id == 1:
            label = 'PrM 1, Internal, Long'
        elif prm_id == 2:
            label = 'PrM 2, Internal, Short'
        elif prm_id == 3:
            label = 'PrM 3, Inline, Long'

        df = df.query(f'prm_id == {prm_id}')

        _, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 8))

        ax.plot(df['date'], df['lifetime'], label=label, linestyle='None', marker="o", markersize=5)

        ax.set_ylabel(r'Lifetime [$ms$]',fontsize=16)
        ax.set_xlabel('Time',fontsize=16)
        ax.tick_params(labelsize=12)
        ax.grid(True)

        ax.set_title('Preliminary', loc='right', color='gray')
        ax.legend(fontsize=12, loc=3)

        ax.set_ylim([0.050, 0.220])

        plt.xticks(rotation=70)

        plt.tight_layout()

        if self._plot_savedir is not None:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            filename = self._plot_savedir + f'prm{prm_id}_lifetime_{timestr}.png'
            plt.savefig(filename)
            self._logger.info(f'Plot saved to {filename}.')
            self._current_plots = {prm_id: filename}

        # plt.show()


    def _send_to_ecl(self):

        if self._current_plots:

            password = self._read_ecl_password()

            ecl = ECL(url='https://dbweb9.fnal.gov:8443/ECL/sbnd/E', user='sbndprm', password=password)

            text=f'<font face="arial"> <b>Purity Monitors Automated Plots</b> <BR> {self._config["ecl_text"]}</font>'

            entry = ECLEntry(category='Purity Monitors', text=text, preformatted=True)

            for prm_id, filename in self._current_plots.items():
                entry.add_image(name=f'lifetime_prm_id_{prm_id}', filename=filename, caption='Lifetime, PrM 2')

            print(entry.show())

            if self._config['post_to_ecl']:
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
