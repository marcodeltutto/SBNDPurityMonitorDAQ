#!/usr/bin/env python3

'''
The main DAQ GUI driver
'''

import os
import sys
import time
import argparse
from PyQt5 import QtGui, QtWidgets
import yaml
import qdarkstyle

from sbndprmdaq.mainwindow import MainWindow
from sbndprmdaq.prmlogger import get_logging, PrMLogWidget

os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"]             = "1"

parser = argparse.ArgumentParser(description='SBND Purity Monitor DAQ')
parser.add_argument('--mock', action='store_true',
                    default=False,
                    help='If true, runs a mock application for debugging purposes.')
parser.add_argument('--datafiles',
                    default='',
                    help='Path where data files will be saved.')
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
# Get the settings from the settings file
#
settings = os.path.join(os.path.dirname(__file__), 'settings.yaml')

with open(settings, encoding="utf-8") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
if args.datafiles:
    config["data_files_path"] = args.datafiles
print('Config:', yaml.dump(config), sep='\n')

# logger.info(yaml.dump(config))


#
# Check Hertbeat
#
heartbeat_file_name = config['data_files_path'] + '/heartbeat.txt'

if os.path.exists(heartbeat_file_name):

    with open(heartbeat_file_name, encoding="utf-8") as f:
        for line in f:
            time_stamp = float(line)

        if abs(time_stamp - time.time()) < 5:
            print('timestamp  :', time_stamp)
            print('time.time():', time.time())
            print('Another DAQ is running on this data directory:', config['data_files_path'])
            print('Either stop the other DAQ, or use a different path.')
            sys.exit(0)



#
# Construct the GUI
#
app = QtWidgets.QApplication(sys.argv)
logs = PrMLogWidget()
window = MainWindow(logs=logs)
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
window.show()


#
# Construct the manager
#
if args.mock:
    from sbndprmdaq.mock_manager import MockPrMManager
    manager = MockPrMManager(config, window)
else:
    from sbndprmdaq.manager import PrMManager
    manager = PrMManager(config, window)

# manager.test()


#
# Pass the manager to the mainwindow
#
window.set_manager(manager)


#
# Set a unique font
#
font = QtGui.QFont("Tahoma", 8)
app.setFont(font)



#
# Take it away
#
app.exec_()
