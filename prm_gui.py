#!/usr/bin/env python3

import sys
import argparse
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph
import qdarkstyle

from sbndprmdaq.mainwindow import MainWindow
from sbndprmdaq.prmlogger import get_logging, PrMLogWidget

parser = argparse.ArgumentParser(description='SBND Purity Monitor DAQ')
parser.add_argument('--mock', action='store_true',
                    default=False,
                    help='If true, runs a mock application for debugging purposes.')
parser.add_argument('--logfile',
                    default='prm_log.txt',
                    help='File name where logs will be saved.')

args = parser.parse_args()


#
# Start the logger
#
logging = get_logging(args.logfile)
logger = logging.getLogger(__name__)
logger.info('SBND Purity Monitor starts.')


#
# Construct the GUI
#
app = QtWidgets.QApplication(sys.argv)
logs = PrMLogWidget()
window = MainWindow(logs=logs)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
window.show()


#
# Construct the manager
#
if args.mock:
    from sbndprmdaq.mock_manager import MockPrMManager
    manager = MockPrMManager()
else:
    from sbndprmdaq.manager import PrMManager
    manager = PrMManager()

# manager.test()


#
# Pass the manager to the mainwindow
#
window.set_manager(manager)


#
# Take it away
#
app.exec_()
