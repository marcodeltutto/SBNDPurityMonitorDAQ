'''
This file contains the basic classes needed for threading
'''
import traceback, sys
from PyQt5.QtCore import *


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `parameter`, `object` data returned from processing: parameter, value
    progress
        `int` indicating % progress (currently not used)
    '''
    finished = pyqtSignal(int, bool) # prm_id, status
    error = pyqtSignal(tuple)
    # result = pyqtSignal(object, object)
    result = pyqtSignal(object)
    progress = pyqtSignal(int, object, int) # prm_id, name, percentage



class Worker(QRunnable):
    '''
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
        # self.kwargs['data_callback'] = self.signals.result

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit(result['prm_id'], result['status'])  # Done