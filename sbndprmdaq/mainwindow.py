import os
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

ICON_RED_LED = os.path.join(os.path.dirname(
               os.path.realpath(__file__)),
               'icons/led-red-on.png')
ICON_GREEN_LED = os.path.join(os.path.dirname(
                 os.path.realpath(__file__)),
                 'icons/green-led-on.png')

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, logs):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "mainwindow.ui")

        uic.loadUi(uifile, self)

        self._logs = logs

        self._prm_id = 2

        self._start_stop_btn.clicked.connect(self._start_stop_prm)
        self._running = False

        self._hv_toggle.setName('HV')
        self._hv_toggle.clicked.connect(self._set_hv)

        self._logs_btn.clicked.connect(self._logs.show)

        self._prm_manager = None

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_status)
        self._status_timer.start(1000)

        self._graph_a = self._plot.plot()
        self._graph_b = self._plot.plot()
        self._plot.setLabel(axis='left', text='Signal [V]')
        self._plot.setLabel(axis='bottom', text='Time [s]')


    def set_manager(self, manager):
        '''
        Sets the purity monitor manager
        '''
        self._prm_manager = manager


    def _start_stop_prm(self):

        self._running = not self._running

        if self._running:
            self._start_prm()
        else:
            self._stop_prm()


    def _start_prm(self):
        self._prm_manager.start_prm(self._prm_id)
        self._start_stop_btn.setText("Stop")
        self._run_status_label.setText('Running')
        self._status_led.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        self.repaint()


    def _stop_prm(self):
        self._prm_manager.stop_prm(self._prm_id)
        self._start_stop_btn.setText("Start")
        self._run_status_label.setText('Not Running')
       	self._status_led.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        self.repaint()


    def _set_hv(self):
        if self._hv_toggle.isChecked():
            self._prm_manager.hv_on()
        else:
            self._prm_manager.hv_off()

    def _check_status(self):
        '''
        Callback that checks the status
        '''
        if self._prm_manager.digitizer_busy():
            self._digi_status_label.setText('Busy')
            self._digi_status_label.setStyleSheet("color: red;")
            self.repaint()
        else:
            self._digi_status_label.setText('Ready')
            self._digi_status_label.setStyleSheet("color: green;")
            self.repaint()

        data = self._prm_manager.get_data(self._prm_id)
        # print('From mainwindow', data)

        if data is None:
            return

        for el in data['A']:
            print('av of el in data A', np.mean(el))

        for el in data['B']:
            print('av of el in data B', np.mean(el))

        if 'A' in data and data['A'] is not None:
            print('------------------------------ len data', len(data['A']))
            av_waveform = data['A'][2] #np.mean(data['A'], axis=0)
            print('------------------------------ len av_waveform', len(av_waveform))
            x = np.arange(len(av_waveform)) / self._prm_manager.ats_samples_per_sec()
            y = av_waveform
            self._graph_a.setData(x, y, pen=pg.mkPen('b'))

        if 'B' in data and data['B'] is not None:
            av_waveform = data['B'][2] #np.mean(data['B'], axis=0)
            x = np.arange(len(av_waveform)) / self._prm_manager.ats_samples_per_sec()
            y = av_waveform
            self._graph_b.setData(x, y, pen=pg.mkPen('r'))



