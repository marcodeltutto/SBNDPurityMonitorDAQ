from pytestqt.qt_compat import qt_api
import pytest

from PyQt5 import QtCore, QtGui, QtWidgets

from sbndprmdaq.mainwindow import MainWindow
# from sbndprmdaq.parallel_communication.mock_communicator import MockCommunicator
from sbndprmdaq.mock_manager import MockPrMManager
from sbndprmdaq.prmlogger import PrMLogWidget


def test_simple(qtbot):
    assert qt_api.QApplication.instance() is not None

    logs = PrMLogWidget()
    qtbot.addWidget(logs)

    # comm = MockCommunicator()
    manager = MockPrMManager()

    window = MainWindow(logs=logs)
    window.set_manager(manager)
    qtbot.addWidget(window)

    for i in [1, 2, 3]:
        qtbot.mouseClick(window._prm_controls[i]._start_stop_btn, QtCore.Qt.LeftButton)
        assert window._prm_controls[i]._run_status_label.text() == 'Running'

        qtbot.mouseClick(window._prm_controls[i]._start_stop_btn, QtCore.Qt.LeftButton)
        assert window._prm_controls[i]._run_status_label.text() == 'Not Running'