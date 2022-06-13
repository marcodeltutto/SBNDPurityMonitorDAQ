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


class SinglePrMDigitizerSettings(QtWidgets.QMainWindow):

    def __init__(self, prm_id=1, name='PrM 1', description='Cryo Bottom'):
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "single_prm_digitizer_settings.ui")

        uic.loadUi(uifile, self)

        self._id = prm_id
        self._name = name
        self._description = description
        self._name_label.setText(self._name)
        self._description_label.setText(description)

    def get_id(self):
        return self._id

    def get_values(self):
        return {
            'number_acquisitions': self._n_acquisitions.text(),
        }



class BaseSettings(QtWidgets.QMainWindow):

    def __init__(self, parent=None, uifile_name=None):
        super(BaseSettings, self).__init__(parent)

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            uifile_name)

        uic.loadUi(uifile, self)

        self._parent = parent

        self._quit_btn.clicked.connect(self.hide)
        self._save_btn.clicked.connect(self.save)
        self._save_quit_btn.clicked.connect(self.save_quit)



        # self._prm_settings = {
        #     1: SinglePrMHVSettings(prm_id=1, name='PrM 1', description='Cryo Bottom'),
        #     2: SinglePrMHVSettings(prm_id=2, name='PrM 2', description='Cryo Top'),
        #     3: SinglePrMHVSettings(prm_id=3, name='PrM 3', description='Inline'),
        # }

        # for s in self._prm_settings.values():
        #     self.setup_settings(s)
        #     self._settings_layout.addWidget(s)

    # def set_hv_control(self, hv_control):
    #     self._hv_control = hv_control

    # def get_prm(prm_id=1):
    #     return self._prm_settings[prm_id]


    # def setup_settings(self, s):
    #     prm_id = s.get_id()
    #     s.setStyleSheet("background-color: rgba(0,0,0,0.1);")

    def values(self):
        return

    def save(self):
        self.save_settings()
        self._parent._status_bar.showMessage('Saved.')
        self._clear_statusbar(delay=5)


    def save_quit(self):
        self.save_settings()
        self._parent._status_bar.showMessage('Saved.')
        self._clear_statusbar(delay=5)
        self.hide()

    def save_settings(self):
        return


    def _clear_statusbar(self, delay=0):
        QtCore.QTimer.singleShot(delay * 1000, lambda: self._parent._status_bar.showMessage(''))





class HVSettings(BaseSettings):

    def __init__(self, parent=None):
        super(HVSettings, self).__init__(parent, "hvsettings.ui")


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

    def save_settings(self):
        values = self.values()
        for prm_id, values in values.items():
            print(prm_id, values)

            for name, value in values.items():
                if name == 'cathode_hv':
                    self._hv_control.set_hv_value('neg', value, prm_id)
                elif name == 'anode_hv':
                    self._hv_control.set_hv_value('pos', value, prm_id)
                else:
                    print(name, value)
                    raise Exception('Not an option')




class DigitizerSettings(BaseSettings):

    def __init__(self, parent=None):
        super(DigitizerSettings, self).__init__(parent, "digitizersettings.ui")


        self._prm_settings = {
            1: SinglePrMDigitizerSettings(prm_id=1, name='PrM 1', description='Cryo Bottom'),
            2: SinglePrMDigitizerSettings(prm_id=2, name='PrM 2', description='Cryo Top'),
            3: SinglePrMDigitizerSettings(prm_id=3, name='PrM 3', description='Inline'),
        }

        for s in self._prm_settings.values():
            self.setup_settings(s)
            self._settings_layout.addWidget(s)

    def set_digitizer_control(self, digitizer):
        self._digitizers = digitizer

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

    def save_settings(self):
        values = self.values()
        for prm_id, values in values.items():
            print(prm_id, values)

            if prm_id not in self._digitizers:
                continue

            for name, value in values.items():
                if name == 'number_acquisitions':
                    self._digitizers[prm_id].set_number_acquisitions(value)
                else:
                    print(name, value)
                    raise Exception('Not an option')



