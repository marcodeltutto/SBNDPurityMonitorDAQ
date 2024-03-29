'''
This file contains the basic classes needed for threading
'''
import traceback
import sys
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished No data
    error `tuple` (exctype, value, traceback.format_exc() )
    result `parameter`, `object` data returned from processing: parameter, value
    progress `int` indicating % progress (currently not used)
    '''
    finished = pyqtSignal(list, list) # prm_id, status
    error = pyqtSignal(tuple)
    # result = pyqtSignal(object, object)
    result = pyqtSignal(object)
    progress = pyqtSignal(int, object, int) # prm_id, name, percentage
    data = pyqtSignal(object) # data dict



class Worker(QRunnable):
    '''
    Worker thread. Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    '''
    # pylint: disable=too-few-public-methods,bare-except

    def __init__(self, fn, *args, **kwargs):
        '''
        Contructor.

        Args:
            fn (function): The callback function to run in the thread.
            args: Arguments to pass to the callback function.
            kwargs: Arguments to pass to the callback function.
        '''
        ####### pylint: disable=invalid-name
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['data_callback'] = self.signals.data

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        result = {'prm_ids': None, 'statuses': None}

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        # else:
            # self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit(result['prm_ids'], result['statuses'])  # Done
