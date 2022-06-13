import os
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


class SinglePrMHVSettings(QtWidgets.QMainWindow):

    def __init__(self, prm_id=1, name='PrM 1', description='Cryo Bottom'):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "single_prm_hv_settings.ui")

        uic.loadUi(uifile, self)

        self._id = prm_id
        self._name = name
        self._description = description
        self._name_label.setText(self._name)
        self._description_label.setText(description)
        self._hv_toggle.setName('HV')

    def get_id(self):
        return self._id

    def get_values(self):
        return {
            'cathode_hv': self._cathode_hv.text(),
            'anode_hv': self._anode_hv.text(),
        }


class HVSettings(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(HVSettings, self).__init__(parent)

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "hvsettings.ui")

        uic.loadUi(uifile, self)

        self._parent = parent

        self._quit_btn.clicked.connect(self.hide)
        self._save_btn.clicked.connect(self.save)
        self._save_quit_btn.clicked.connect(self.save_quit)



        self._prm_settings = {
            1: SinglePrMHVSettings(prm_id=1, name='PrM 1', description='Cryo Bottom'),
            2: SinglePrMHVSettings(prm_id=2, name='PrM 2', description='Cryo Top'),
            3: SinglePrMHVSettings(prm_id=3, name='PrM 3', description='Inline'),
        }

        for s in self._prm_settings.values():
            self.setup_settings(s)
            self._settings_layout.addWidget(s)

    def set_hv_control(self, hv_control):
        self._hv_control = hv_control

    def get_prm(prm_id=1):
        return self._prm_settings[prm_id]


    def setup_settings(self, s):
        prm_id = s.get_id()
        s.setStyleSheet("background-color: rgba(0,0,0,0.1);")

    def values(self):
        ret = {}
        for k, v in self._prm_settings.items():
            ret[k] = v.get_values()

        return ret

    def save(self):
        self._parent.save_settings(self.values())
        self._parent._status_bar.showMessage('Saved.')
        self._clear_statusbar(delay=5)


    def save_quit(self):
        self._parent.save_settings(self.values())
        self._parent._status_bar.showMessage('Saved.')
        self._clear_statusbar(delay=5)
        self.hide()


    def _clear_statusbar(self, delay=0):
        QtCore.QTimer.singleShot(delay * 1000, lambda: self._parent._status_bar.showMessage(''))


