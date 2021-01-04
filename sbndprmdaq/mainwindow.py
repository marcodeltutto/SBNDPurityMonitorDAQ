import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer

ICON_RED_LED = os.path.join(os.path.dirname(
               os.path.realpath(__file__)),
               'icons/led-red-on.png')
ICON_GREEN_LED = os.path.join(os.path.dirname(
                 os.path.realpath(__file__)),
                 'icons/green-led-on.png')

class Control(QtWidgets.QMainWindow):

    def __init__(self, prm_id=0, name='PrM 0'):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "controls.ui")

        uic.loadUi(uifile, self)

        self._id = prm_id
        self._name = name
        self._name_label.setText(self._name)
        self._mode_toggle.setNames('Auto', 'Manual')
        self._mode_toggle.isSimpleOption()

    def get_id(self):
        return self._id

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, logs):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "mainwindow.ui")

        uic.loadUi(uifile, self)

        self._logs = logs

        # self._start_stop_btn.clicked.connect(self._start_stop_prm)
        self._running = [False, False, False]

        # self._hv_toggle.setName('HV')
        # self._hv_toggle.clicked.connect(self._set_hv)

        self._logs_btn.clicked.connect(self._logs.show)

        self._prm_manager = None

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_status)
        self._status_timer.start(1000)

        self._prm_controls = []
        self._prm_controls.append(Control(prm_id=0, name='PrM 0'))
        self._prm_controls.append(Control(prm_id=1, name='PrM 1'))
        self._prm_controls.append(Control(prm_id=2, name='PrM 2'))
        # self._prm_controls[0].setStyleSheet("background-color: rgba(0,0,0,0.1);")

        for control in self._prm_controls:
            self.setup_control(control)
            self._vertical_layout.addWidget(control)

    def setup_control(self, control):
        prm_id = control.get_id()
        control.setStyleSheet("background-color: rgba(0,0,0,0.1);")
        control._start_stop_btn.clicked.connect(lambda: self._start_stop_prm(prm_id=prm_id))
        control._mode_toggle.clicked.connect(lambda: self._set_mode(prm_id=prm_id))


    def set_manager(self, manager):
        '''
        Sets the purity monitor manager
        '''
        self._prm_manager = manager


    def _start_stop_prm(self, prm_id):

        self._running[prm_id] = not self._running[prm_id]

        if self._running[prm_id]:
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
        for i, control in enumerate(self._prm_controls):
            if self._prm_manager.digitizer_busy(i):
                control._digi_status_label.setText('Busy')
                control._digi_status_label.setStyleSheet("color: red;")
                self.repaint()
            else:
                control._digi_status_label.setText('Ready')
                control._digi_status_label.setStyleSheet("color: green;")
                self.repaint()

