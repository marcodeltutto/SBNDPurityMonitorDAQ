from __future__ import division
import ctypes
import numpy as np
import os
import signal
import sys
import time
import logging


class ATS310Exception(Exception):
    """
    Exception class for ATS310.
    """

    def __init__(self, logger, message):
        '''
        Contructor.

        Args:
            logger (PrMLogger): The logger widget.
            message (str): The error message to display.
        '''
        self._message = message
        logger.critical(self._message)
        super(ESP32Exception, self).__init__(self._message)


def get_digitizers(prm_id_to_ats_systemid):
    '''
    Returns all the available digitizers (mock)

    Args:
        prm_id_to_ats_systemid (dict): A dictionary from PrM ID to digitized systemId.

    Returns:
        list: A list of digitizers
    '''

    digitizers = {}
    for prm_id, systemid in prm_id_to_ats_systemid.items():

        ats310 = MockATS310()

        # Simulate that prm 3 is not available
        if prm_id == 3:
            ats310 = None
        digitizers[prm_id] = ats310

    return digitizers


class MockBoard():
    def __init__(self):
        self._status = False

    def startCapture(self):
        print('Capture start.')
        self._status = True

    def busy(self):
        return self._status


class MockATS310():
    '''
    This class controls a mock ATS310 digitizer.
    '''

    def __init__(self):
        '''
        Constructor.

        Args:
            systemId (int): The system ID
            boardId (int): The board ID
        '''
        self._logger = logging.getLogger(__name__)

        self._board = MockBoard()
        # self._board = BoardWrapper(self._board, ATS310Exception)

        self._samples_per_sec = 20000000.0


    def get_samples_per_second(self):
        '''
        Getter for the samples per seconds the digitizer is acquiring.

        Returns:
            int: Number of samples per second.
        '''
        return self._samples_per_sec


    def start_capture(self):
        '''
        Starts a digitizer capture.
        '''
        start = time.time() # Keep track of when acquisition started
        self._board.startCapture() # Start the acquisition
        self._board._status = True


    def check_capture(self, prm_id=1, progress_callback=None):
        '''
        Checks for a capture to finish.

        Args:
            prm_id (int): The purity monitor ID (for logging).
            progress_callback (function): The callback for progress (for logging).
        '''
        # Simulate the time it takes to get the trigger
        simulated_time = 4 #seconds
        start = time.time()
        while(simulated_time > time.time() - start):
            perc = (time.time() - start) / simulated_time * 100
            if progress_callback is not None:
                progress_callback.emit(prm_id, 'Check Capture', perc)
            time.sleep(0.1)
        return True

    def busy(self):
        '''
        Returns if the ats310 board is busy or not.

        Returns:
            bool: True if busy, False otherwise.
        '''
        return self._board.busy()

