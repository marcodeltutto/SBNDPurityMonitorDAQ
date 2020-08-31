import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow import MainWindow
from communicator import Communicator

comm = Communicator()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(comm)
window.show()
app.exec_()