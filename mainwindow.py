from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

ICON_RED_LED='icons/led-red-on.png'
ICON_GREEN_LED='icons/green-led-on.png'

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, comm, logs):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)

        self._comm = comm
        self._logs = logs

        self._start_stop_btn.clicked.connect(self._start_stop_prm)
        self._running = False

        self._hv_toggle.setName('HV')
        self._hv_toggle.clicked.connect(self._set_hv)

        self._logs_btn.clicked.connect(self._logs.show)


    def _start_stop_prm(self):

        self._running = not self._running

        if self._running:
            self._start_prm()
        else:
            self._stop_prm()


    def _start_prm(self):
        self._comm.start_prm()
        self._start_stop_btn.setText("Stop")
        self._run_status_label.setText('Running')
        self._status_led.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        self.repaint()


    def _stop_prm(self):
        self._comm.stop_prm()
        self._start_stop_btn.setText("Start")
        self._run_status_label.setText('Not Running')
       	self._status_led.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        self.repaint()


    def _set_hv(self):
        if self._hv_toggle.isChecked():
            self._comm.hv_on()
        else:
            self._comm.hv_off()