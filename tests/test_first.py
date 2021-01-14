import os
import yaml
from pytestqt.qt_compat import qt_api
import pytest

from PyQt5 import QtCore, QtGui, QtWidgets

from sbndprmdaq.mainwindow import MainWindow
from sbndprmdaq.parallel_communication.mock_communicator import MockCommunicator
from sbndprmdaq.mock_manager import MockPrMManager
from sbndprmdaq.prmlogger import PrMLogWidget

settings = os.path.join(os.path.dirname(__file__), '../settings.yaml')

with open(settings) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)



def test_instantiate_communicator():
    comm = MockCommunicator()


def test_instantiate_manager():
    manager = MockPrMManager(config)


def test_simple_2(qtbot):
    assert qt_api.QApplication.instance() is not None

    logs = PrMLogWidget()
    qtbot.addWidget(logs)

    window = MainWindow(logs=logs)
    qtbot.addWidget(window)

    manager = MockPrMManager(config, window)
    window.set_manager(manager)


    for i in [1, 2]:
        qtbot.mouseClick(window._prm_controls[i]._start_stop_btn, QtCore.Qt.LeftButton)
        assert window._prm_controls[i]._run_status_label.text() == 'Running'
