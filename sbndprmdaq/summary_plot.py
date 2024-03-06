
import logging
import datetime
import pandas as pd
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt

class SummaryPlot:

    def __init__(self, config):

        self._timer = None

        self._dataframe_filename = None

        self._first_day = "02/20/2024"

        self._config = config['summary_plot']

        self._logger = logging.getLogger(__name__)


        if self._config['make_summary_plots']:

            seconds_to_start = self.seconds_until_hour(self._config['start_hour'])
            seconds_to_start = 5
            QTimer.singleShot(seconds_to_start * 1000, self.start_periodic_plotting)

            self._logger.info(f'The first summary plot will be made in {seconds_to_start/3600:.2f} hours.')


    def start_periodic_plotting(self):

        self._logger.info(f'Making the first summary plot.')
        
        self.make_summary_plots()

        self._timer = QTimer()
        self._timer.timeout.connect(self.make_summary_plots)
        self._timer.start(self._config['time_interval'] * 1000 * 3600)


    def set_dataframe_path(self, dataframe_filename):

        self._dataframe_filename = dataframe_filename

    def set_plot_savedir(self, plot_savedir):

        self._plot_savedir = plot_savedir


    def make_summary_plots(self):

        if self._dataframe_filename is None:
            self._logger.warning(f'Dont have a dataframe filename. Plot will not be made.')
            return

        df = pd.read_csv(self._dataframe_filename)

        df['date'] = pd.to_datetime(df['date'])

        # Select entries past a certain day
        first_day = datetime.datetime.strptime(self._first_day, "%m/%d/%Y")

        mask = df['date'] > first_day
        df = df[mask]

        for prm_id in self._config['prms']:
            self._make_summary_plot(prm_id, df)


    def _make_summary_plot(self, prm_id, df):

        label = ''
        if prm_id == 1:
            label = 'PrM 1, Internal, Long'
        elif prm_id == 2:
            label = 'PrM 2, Internal, Short'
        elif prm_id == 3:
            label = 'PrM 3, Inline, Long'

        df = df.query(f'prm_id == {prm_id}')

        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 8))

        ax.plot(df['date'], df['lifetime'], label='PrM 2, Internal, Short', linestyle='None', marker="o", markersize=5)

        ax.set_ylabel(r'Lifetime [$ms$]',fontsize=16)
        ax.set_xlabel('Time',fontsize=16)
        ax.tick_params(labelsize=12)
        ax.grid(True)

        ax.set_title('Preliminary', loc='right', color='gray')
        ax.legend(fontsize=12, loc=3)

        ax.set_ylim([0.050, 0.220])

        plt.xticks(rotation=70)

        plt.tight_layout()
        plt.savefig(self._plot_savedir + f'prm{prm_id}_lifetime_{self._first_day}_now.pdf')
        # plt.show()



    def seconds_until_hour(self, target_hour):
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





