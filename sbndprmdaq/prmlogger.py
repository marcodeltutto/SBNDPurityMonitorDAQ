'''
Logging tools.
'''
import sys
import logging
from PyQt5 import QtWidgets


def get_logging(filename):
    '''
    Returns a logging properly setup to use.
    '''
    logging.basicConfig(filename=filename,
                        filemode='w',
                        level=logging.INFO,
                        # format='%(asctime)s %(levelname)-8s %(message)s',
                        format='%(asctime)s - %(levelname)-8s %(name)s - %(message)s')

    # Remove the qdarkstyle logger, not needed
    logging.getLogger('qdarkstyle').propagate = False

    # Change formatting for stream handler
    # formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
    # sh = logging.StreamHandler()
    # sh.setFormatter(formatter)
    # logging.getLogger().addHandler(sh)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


    return logging




class QTextEditLogger(logging.Handler):
    '''
    A loggin handler with a text widget where the logs
    will be placed.
    '''
    def __init__(self, parent):
        '''
        Constructor.

        Args:
            parent (QtWidget): The parent widget.
        '''
        super().__init__()
        self._widget = QtWidgets.QPlainTextEdit(parent)
        self._widget.setReadOnly(True)


    def get_widget(self):
        '''
        Getter for the text widget.

        Returns:
            QtWidget: the text widget.
        '''
        return self._widget


    def emit(self, record):
        '''
        Emitter.

        Args:
            record (str): the text.
        '''
        msg = self.format(record)
        self._widget.appendPlainText(msg)


class PrMLogWidget(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    '''
    A window to display the logs
    '''

    def __init__(self, parent=None):
        '''
        Constructor.

        Args:
            parent (QtWidget): The parent widget.
        '''
        super().__init__(parent)

        log_text_box = QTextEditLogger(self)
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s %(name)s - %(message)s')
        log_text_box.setFormatter(formatter)
        logging.getLogger().addHandler(log_text_box)


        self._button = QtWidgets.QPushButton(self)
        self._button.setText('Close')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(log_text_box.get_widget())
        layout.addWidget(self._button)
        self.setLayout(layout)

        self._button.clicked.connect(self.hide)
