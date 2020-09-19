#!/usr/bin/env python3

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph
import qdarkstyle
from mainwindow import MainWindow
import argparse
from prmlogger import get_logging

parser = argparse.ArgumentParser(description='SBND Purity Monitor DAQ')
parser.add_argument('--mock', action='store_true',
                    default=False,
                    help='If true, runs a mock application for debugging purposes.')
parser.add_argument('--logfile',
                    default='prm_log.txt',
                    help='File name where logs will be saved.')

args = parser.parse_args()

logging = get_logging(args.logfile)
logger = logging.getLogger(__name__)
logger.info('SBND Purity Monitor starts.')

if args.mock:
	from mock_communicator import MockCommunicator
	comm = MockCommunicator()
else:
	from communicator import Communicator
	comm = Communicator()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(comm)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
window.show()
app.exec_()