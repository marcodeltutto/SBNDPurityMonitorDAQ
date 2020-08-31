from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

ICON_RED_LED='icons/led-red-on.png'
ICON_GREEN_LED='icons/green-led-on.png'

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, comm):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)

        self._comm = comm

        self._start_btn.clicked.connect(self._start_prm)
        self._stop_btn.clicked.connect(self._stop_prm)



    def _start_prm(self):
        self._comm.start_prm()
        self._run_status_label.setText('Running')
        self._status_led.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        self.repaint()

    def _stop_prm(self):
        self._comm.stop_prm()
        self._run_status_label.setText('Not Running')
       	self._status_led.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        self.repaint()