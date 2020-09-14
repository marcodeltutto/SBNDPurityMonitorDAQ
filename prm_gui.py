import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph

from mainwindow import MainWindow
from communicator import Communicator
from mock_communicator import MockCommunicator

import argparse
parser = argparse.ArgumentParser(description='SBND Purity Monitor DAQ')
parser.add_argument('--mock', action='store_true',
                    default=False,
                    help='If true, runs a mock application for debugging purposes.')

args = parser.parse_args()

if args.mock:
	comm = MockCommunicator()
else:
	comm = Communicator()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(comm)
window.show()
app.exec_()