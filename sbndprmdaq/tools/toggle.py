"""
Toggle helper.
An toggle is a custom, big toggle button.
"""

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRect, pyqtSignal


class Toggle(QtWidgets.QPushButton):
    """
    This is custom QPushButton that renders as a toggle
    """

    valueChanged = pyqtSignal()

    def __init__(self, parent=None, name=None):
        """
        Constructor
        arguments:
        - parent: the parent widget
        """

        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)
        self._name = name
        self._name1 = None
        self._name2 = None
        self._simple_option = False

    def set_name(self, name):
        '''
        Sets the Toggle name
        '''
        self._name = name
        self._name1 = None
        self._name2 = None

    def set_names(self, name1, name2):
        '''
        Sets the Toggle names
        '''
        self._name1 = name1
        self._name2 = name2
        self._name = None

    def is_simple_option(self, simple_option=True):
        '''
        Sets if this Toggle is a simple option (shown in grey)
        or if a red/green toggle is needed.
        '''
        self._simple_option = simple_option

    def paintEvent(self, event):
        #pylint: disable=invalid-name
        #pylint: disable=unused-argument
        """
        Reimplement the QPushButton.paintEvent function
        arguments:
        - event: the event
        """

        if self._name:
            label = f'{self._name} ON' if self.isChecked() else f'{self._name} OFF'
        elif self._name1 and self._name2:
            label = f'{self._name1}' if self.isChecked() else f'{self._name2}'
        else:
            label = 'ON' if self.isChecked() else 'OFF'

        if self.isEnabled():
            bg_color = Qt.green if self.isChecked() else Qt.red
            if self._simple_option:
                bg_color = Qt.gray if self.isChecked() else Qt.gray
        else:
            bg_color = Qt.gray

        radius = 18
        width = 60
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QtGui.QColor(0, 0, 0))

        pen = QtGui.QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(
            QRect(-width, -radius, 2 * width, 2 * radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2 * radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)

    def setValue(self, value):
        #pylint: disable=invalid-name
        '''
        Just calls setChecked().
        arguments:
        - value: (bool) the value to set
        '''
        if value is None:
            return None
        return self.setChecked(value)

    def value(self):
        '''
        Just calls isChecked().
        '''
        return int(self.isChecked())
