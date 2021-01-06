import os
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from sbndprmdaq.prm_settings.settings import Settings

ICON_RED_LED = os.path.join(os.path.dirname(
               os.path.realpath(__file__)),
               'icons/led-red-on.png')
ICON_GREEN_LED = os.path.join(os.path.dirname(
                 os.path.realpath(__file__)),
                 'icons/green-led-on.png')

class Control(QtWidgets.QMainWindow):

    def __init__(self, prm_id=1, name='PrM 1', description='Cryo Bottom'):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "controls.ui")

        uic.loadUi(uifile, self)

        self._id = prm_id
        self._name = name
        self._description = description
        self._name_label.setText(self._name)
        self._description_label.setText(description)
        self._mode_toggle.setNames('Auto', 'Manual')
        self._mode_toggle.isSimpleOption()
        self._running = False

        self._progress_bar.setValue(0)
        self._progress_label.setText('')

    def get_id(self):
        return self._id

    def set_progress(self, name, perc, **kwargs):
        name = str(name)
        if perc > 100 or perc < 0:
            raise Exception('perc can pnly be between 0 and 100')

        self._progress_label.setText(name)
        self._progress_bar.setValue(perc)

        if 'color' in kwargs:
            self._progress_label.setStyleSheet("color: " + kwargs['color']);


    def reset_progress(self, name=None, **kwargs):
        self._progress_bar.setValue(0)

        if name is not None:
            self._progress_label.setText(name)
        else:
            self._progress_label.setText('')

        if 'color' in kwargs:
            self._progress_label.setStyleSheet("color: " + kwargs['color']);

class DataDisplay(QtWidgets.QMainWindow):

    def __init__(self, prm_id=1, name='PrM 1'):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "data_display.ui")

        uic.loadUi(uifile, self)

        self._id = prm_id
        self._name = name
        self._name_label.setText(self._name)

    def get_id(self):
        return self._id

    def set_latest_data(self, qa, qc, tau, time):
        text = f'Qa = {qa}\nQc = {qc}\nLifetime = {tau}'
        self._text.setText(text)
        self._date.setText(time.strftime("%B %d, %Y  %H:%M:%S"))


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, logs):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "mainwindow.ui")

        uic.loadUi(uifile, self)

        self._logs = logs

        self._logs_btn.clicked.connect(self._logs.show)

        self._settings = Settings(self)
        self._settings_btn.clicked.connect(self._settings.show)

        self._prm_manager = None

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_status)
        self._status_timer.start(1000)

        self._prm_controls = {
            1: Control(prm_id=1, name='PrM 1', description='Cryo Bottom'),
            2: Control(prm_id=2, name='PrM 2', description='Cryo Top'),
            3: Control(prm_id=3, name='PrM 3', description='Inline'),
        }
        # self._prm_controls[0].setStyleSheet("background-color: rgba(0,0,0,0.1);")

        self._graphs = {}
        self._show_graph = {'all': False}

        for control in self._prm_controls.values():
            self.setup_control(control)
            self._controls_layout.addWidget(control)
            self._graphs[control.get_id()] = {
                'A': self._plot.plot(),
                'B': self._plot.plot(),
            }
            self._show_graph[control.get_id()] = False

        # self._graph_a = self._plot.plot()
        # self._graph_b = self._plot.plot()
        self._plot.setLabel(axis='left', text='Signal [V]')
        self._plot.setLabel(axis='bottom', text='Time [s]')

        # Connect the checkboxes for plot displaying
        self._show_choice_checkboxes = {
            'all': self._prmall_checkbox,
            1: self._prm1_checkbox,
            2: self._prm2_checkbox,
            3: self._prm3_checkbox,
        }

        self._show_choice_checkboxes['all'].clicked.connect(lambda: self._update_plot_choice('all'))
        self._show_choice_checkboxes[1].clicked.connect(lambda: self._update_plot_choice(1))
        self._show_choice_checkboxes[2].clicked.connect(lambda: self._update_plot_choice(2))
        self._show_choice_checkboxes[3].clicked.connect(lambda: self._update_plot_choice(3))


        self._latest_data = {
            1: DataDisplay(prm_id=1, name='PrM 1'),
            2: DataDisplay(prm_id=2, name='PrM 2'),
            3: DataDisplay(prm_id=3, name='PrM 3'),
        }

        for latest_data in self._latest_data.values():
            self._latest_data_layout.addWidget(latest_data)
            self.setup_latest_data(latest_data)


    def setup_control(self, control):
        prm_id = control.get_id()
        control.setStyleSheet("background-color: rgba(0,0,0,0.1);")
        control._start_stop_btn.clicked.connect(lambda: self.start_stop_prm(prm_id=prm_id))
        control._mode_toggle.clicked.connect(lambda: self._set_mode(prm_id=prm_id))

    def setup_latest_data(self, latest_data):
        prm_id = latest_data.get_id()
        latest_data.setStyleSheet("background-color: rgba(0,0,0,0.1);")



    def _update_plot_choice(self, prm_id):

        # Reset to false
        # for key in self._show_choice_checkboxes.keys():
        #     self._show_graph[key] = False

        if prm_id == 'all':
            if self._prmall_checkbox.isChecked():
                for pid in [1, 2, 3]:
                    self._show_graph[pid] = True
                    self._show_choice_checkboxes[pid].setChecked(False)
            else:
                for pid in [1, 2, 3]:
                    self._show_graph[pid] = False
                    self._show_choice_checkboxes[pid].setChecked(False)

        else:
            if self._show_choice_checkboxes[prm_id].isChecked():
                self._show_graph[prm_id] = True
                self._prmall_checkbox.setChecked(False)
            else:
                self._show_graph[prm_id] = False


    def set_manager(self, manager):
        '''
        Sets the purity monitor manager
        '''
        self._prm_manager = manager

    def set_progress(self, prm_id, name, perc, **kwargs):
        self._prm_controls[prm_id].set_progress(name, perc, **kwargs)

    def reset_progress(self, prm_id, name=None, **kwargs):
        self._prm_controls[prm_id].reset_progress(name, **kwargs)


    def start_stop_prm(self, prm_id):
        print('Start stop prm_id', prm_id)

        self._prm_controls[prm_id]._running = not self._prm_controls[prm_id]._running

        if self._prm_controls[prm_id]._running:
            self._start_prm(prm_id)
        else:
            self._stop_prm(prm_id)


    def _start_prm(self, prm_id):
        self._prm_manager.start_prm(prm_id)
        self._prm_controls[prm_id]._start_stop_btn.setText("Stop")
        self._prm_controls[prm_id]._run_status_label.setText('Running')
        self._prm_controls[prm_id]._status_led.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        self.repaint()


    def _stop_prm(self, prm_id):
        self._prm_manager.stop_prm(prm_id)
        self._prm_controls[prm_id]._start_stop_btn.setText("Start")
        self._prm_controls[prm_id]._run_status_label.setText('Not Running')
       	self._prm_controls[prm_id]._status_led.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        self.repaint()


    def _set_hv(self):
        if self._hv_toggle.isChecked():
            self._prm_manager.hv_on()
        else:
            self._prm_manager.hv_off()

    def _set_mode(self, prm_id):
        control = self._prm_controls[prm_id]
        if control._mode_toggle.isChecked():
            self._prm_manager.set_mode(prm_id, 'auto')
        else:
            self._prm_manager.set_mode(prm_id, 'manual')

    def _check_status(self):
        '''
        Callback that checks the status
        '''
        print('_check_statusm len =', len(self._prm_controls))
        for control in self._prm_controls.values():
            if self._prm_manager.digitizer_busy(control.get_id()):
                control._digi_status_label.setText('Busy')
                control._digi_status_label.setStyleSheet("color: red;")
                self.repaint()
            else:
                control._digi_status_label.setText('Ready')
                control._digi_status_label.setStyleSheet("color: green;")
                self.repaint()

            data = self._prm_manager.get_data(control.get_id())
            # print('From mainwindow', data)
            print('_check_status', control.get_id())

            if data is None:
                continue

            print('--> _check_status', control.get_id())
            # for el in data['A']:
            #     print('av of el in data A', np.mean(el))

            # for el in data['B']:
            #     print('av of el in data B', np.mean(el))

            if 'A' in data and data['A'] is not None:
                # print('------------------------------ len data', len(data['A']))
                av_waveform = data['A'][2] #np.mean(data['A'], axis=0)
                # print('------------------------------ len av_waveform', len(av_waveform))
                x = np.arange(len(av_waveform)) / self._prm_manager.ats_samples_per_sec()
                y = av_waveform
                # self._graph_a.setData(x, y, pen=pg.mkPen('b'))

                if self._show_graph[control.get_id()]:
                    self._graphs[control.get_id()]['A'].setData(x, y, pen=pg.mkPen('b'))
                else:
                    self._graphs[control.get_id()]['A'].setData([], [])

            if 'B' in data and data['B'] is not None:
                av_waveform = data['B'][2] #np.mean(data['B'], axis=0)
                x = np.arange(len(av_waveform)) / self._prm_manager.ats_samples_per_sec()
                y = av_waveform
                # self._graph_b.setData(x, y, pen=pg.mkPen('r'))
                if self._show_graph[control.get_id()]:
                    self._graphs[control.get_id()]['B'].setData(x, y, pen=pg.mkPen('r'))
                else:
                    self._graphs[control.get_id()]['B'].setData([], [])

            qa, qc, tau = self._extract_values(data['A'], data['B'])

            self._latest_data[control.get_id()].set_latest_data(qa, qc, tau, data['time'])

    def _extract_values(self, a, b):
        return 1, 2, 3


