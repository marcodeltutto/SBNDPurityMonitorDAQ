from pytestqt.qt_compat import qt_api
import pytest

from sbndprmdaq.mainwindow import MainWindow
from sbndprmdaq.parallel_communication.mock_communicator import MockCommunicator
from sbndprmdaq.prmlogger import PrMLogWidget


def test_simple(qtbot):
    assert qt_api.QApplication.instance() is not None

    logs = PrMLogWidget()
    qtbot.addWidget(logs)

    comm = MockCommunicator()

    window = MainWindow(comm=comm, logs=logs)
    qtbot.addWidget(window)