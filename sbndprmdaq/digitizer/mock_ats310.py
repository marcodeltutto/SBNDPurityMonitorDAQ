from __future__ import division
# import matplotlib.pyplot as plt
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
        Contructor
        '''
        self._message = message
        logger.critical(self._message)
        super(ESP32Exception, self).__init__(self._message)


class MockBoard():
    def __init__(self):
        self._status = False

    def startCapture(self):
        print('Capture start.')
        self._status = True

    def busy(self):
        return self._status


class MockATS310():

    def __init__(self):
        '''
        Constructor
        '''
        self._logger = logging.getLogger(__name__)

        self._board = MockBoard()
        # self._board = BoardWrapper(self._board, ATS310Exception)

        self._samples_per_sec = 20000000.0


    def start_capture(self):
        start = time.time() # Keep track of when acquisition started
        self._board.startCapture() # Start the acquisition
        self._board._status = True

    def busy(self):
        '''
        Returns if the ats310 board is busy or not
        '''
        return self._board.busy()

    def get_samples_per_second(self):
        return self._samples_per_sec

