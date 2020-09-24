import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

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

        self._start_stop_btn.clicked.connect(self._start_stop_prm)
        self._running = False

        self._hv_toggle.setName('HV')
        self._hv_toggle.clicked.connect(self._set_hv)

        self._logs_btn.clicked.connect(self._logs.show)

        self._prm_manager = None
    #     self._comm = None


    # def set_communicator(self, comm):
    #     '''
    #     Sets the parallel communicator
    #     '''
    #     self._comm = comm


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
        self._prm_manager.start_prm()
        self._start_stop_btn.setText("Stop")
        self._run_status_label.setText('Running')
        self._status_led.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        self.repaint()


    def _stop_prm(self):
        self._prm_manager.stop_prm()
        self._start_stop_btn.setText("Start")
        self._run_status_label.setText('Not Running')
       	self._status_led.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        self.repaint()


    def _set_hv(self):
        if self._hv_toggle.isChecked():
            self._prm_manager.hv_on()
        else:
            self._prm_manager.hv_off()