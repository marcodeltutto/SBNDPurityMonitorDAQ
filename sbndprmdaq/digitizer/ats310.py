from __future__ import division
import matplotlib.pyplot as plt
import ctypes
import numpy as np
import os
import signal
import sys
import time
import logging

from sbndprmdaq.digitizer.board_wrapper import BoardWrapper

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


class ATS310():

    def __init__(self):
        '''
        Constructor
        '''
        self._logger = logging.getLogger(__name__)

        self._board = ats.Board(systemId=1, boardId=1)

        if self._board.handle is None or self._board.handle == 0:
            raise ATS310Exception(self._logger, 'Board handle is None or zero.')

        self._board = BoardWrapper(self._board, ATS310Exception)

        # TODO: Select the number of pre-trigger samples
        self._pre_trigger_samples = 1024

        # TODO: Select the number of samples per record.
        self._post_trigger_samples = 1024

        # TODO: Select the number of records in the acquisition.
        self._records_per_capture = 1

        # TODO: Select the amount of time to wait for the acquisition to
        # complete to on-board memory.
        self._acquisition_timeout_sec = 10

        # TODO: Select the active channels.
        self._channels = ats.CHANNEL_A | ats.CHANNEL_B
        self._channel_count = 0
        for c in ats.channels:
            self._channel_count += (c & self._channels == c)

        self.configure_board()
        self.prepare_acquisition()

    # Configures a board for acquisition
    def configure_board(self):
        # TODO: Select clock parameters as required to generate this
        # sample rate
        #
        # For example: if self._samples_per_sec is 100e6 (100 MS/s), then you can
        # either:
        #  - select clock source INTERNAL_CLOCK and sample rate
        #    SAMPLE_RATE_100MSPS
        #  - or select clock source FAST_EXTERNAL_CLOCK, sample rate
        #    SAMPLE_RATE_USER_DEF, and connect a 100MHz signal to the
        #    EXT CLK BNC connector
        # global self._samples_per_sec
        self._samples_per_sec = 20000000.0
        self._samples_per_sec_id = ats.SAMPLE_RATE_20MSPS

        self._board.setCaptureClock(ats.INTERNAL_CLOCK,
                                    self._samples_per_sec_id,
                                    ats.CLOCK_EDGE_RISING,
                                    0)

        # TODO: Select channel A input parameters as required.
        self._board.inputControlEx(ats.CHANNEL_A,
                                   ats.DC_COUPLING,
                                   # ats.INPUT_RANGE_PM_400_MV,
                                   ats.INPUT_RANGE_PM_40_MV,
                                   # ats.IMPEDANCE_50_OHM)
                                   ats.IMPEDANCE_1M_OHM)

        # TODO: Select channel A bandwidth limit as required.
        self._board.setBWLimit(ats.CHANNEL_A, 0)


        # TODO: Select channel B input parameters as required.
        self._board.inputControlEx(ats.CHANNEL_B,
                                   ats.DC_COUPLING,
                                   # ats.INPUT_RANGE_PM_400_MV,
                                   ats.INPUT_RANGE_PM_40_MV,
                                   # ats.IMPEDANCE_50_OHM)
                                   ats.IMPEDANCE_1M_OHM)

        # TODO: Select channel B bandwidth limit as required.
        self._board.setBWLimit(ats.CHANNEL_B, 0)

        # TODO: Select trigger inputs and levels as required.
        self._board.setTriggerOperation(ats.TRIG_ENGINE_OP_J,
                                        ats.TRIG_ENGINE_J,
                                        # ats.TRIG_CHAN_A,
                                        ats.TRIG_EXTERNAL,
                                        ats.TRIGGER_SLOPE_POSITIVE,
                                        # 150,
                                        200,
                                        ats.TRIG_ENGINE_K,
                                        ats.TRIG_DISABLE,
                                        ats.TRIGGER_SLOPE_POSITIVE,
                                        128)

        # TODO: Select external trigger parameters as required.
        self._board.setExternalTrigger(ats.DC_COUPLING, ats.ETR_TTL) # could be ETR_5V

        # TODO: Set trigger delay as required.
        self._trigger_delay_sec = 0
        self._trigger_delay_samples = int(self._trigger_delay_sec * self._samples_per_sec + 0.5)
        self._board.setTriggerDelay(self._trigger_delay_samples)

        # TODO: Set trigger timeout as required.
        #
        # NOTE: The board will wait for a for this amount of time for a
        # trigger event.  If a trigger event does not arrive, then the
        # board will automatically trigger. Set the trigger timeout value
        # to 0 to force the board to wait forever for a trigger event.
        #
        # IMPORTANT: The trigger timeout value should be set to zero after
        # appropriate trigger parameters have been determined, otherwise
        # the board may trigger if the timeout interval expires before a
        # hardware trigger event arrives.
        self._board.setTriggerTimeOut(0)

        # Configure AUX I/O connector as required
        self._board.configureAuxIO(ats.AUX_OUT_TRIGGER, 0)

    def prepare_acquisition(self):

        # Compute the number of bytes per record and per buffer
        memory_size_samples, bits_per_sample = self._board.getChannelInfo()
        self._bytes_per_sample = (bits_per_sample.value + 7) // 8
        self._samples_per_record = self._pre_trigger_samples + self._post_trigger_samples
        self._bytes_per_record = self._bytes_per_sample * self._samples_per_record

        # Calculate the size of a record buffer in bytes. Note that the
        # buffer must be at least 16 bytes larger than the transfer size.
        self._bytes_per_buffer = (self._bytes_per_sample *
                          (self._samples_per_record + 0))

        # Set the record size
        self._board.setRecordSize(self._pre_trigger_samples, self._post_trigger_samples)

        # Configure the number of records in the acquisition
        self._board.setRecordCount(self._records_per_capture)

    def start_capture(self):
        start = time.time() # Keep track of when acquisition started
        self._board.startCapture() # Start the acquisition
        print("Capturing %d record. Press <enter> to abort" % self._records_per_capture)
        buffersCompleted = 0
        bytesTransferred = 0
        while not ats.enter_pressed():
            if not self._board.busy():
                # Acquisition is done
                break
            if time.time() - start > self._acquisition_timeout_sec:
                self._board.abortCapture()
                raise Exception("Error: Capture timeout. Verify trigger")
            time.sleep(10e-3)

        captureTime_sec = time.time() - start
        recordsPerSec = 0
        if captureTime_sec > 0:
            recordsPerSec = self._records_per_capture / captureTime_sec
        print("Captured %d records in %f rec (%f records/sec)" %
              (self._records_per_capture, captureTime_sec, recordsPerSec))

        sample_type = ctypes.c_uint8
        if self._bytes_per_sample > 1:
            sample_type = ctypes.c_uint16

        buffer = ats.DMABuffer(self._board.handle, sample_type, self._bytes_per_buffer + 16)

        # Transfer the records from on-board memory to our buffer
        print("Transferring %d records..." % self._records_per_capture)

        for record in range(self._records_per_capture):
            if ats.enter_pressed():
                break
            for channel in range(self._channel_count):
                channel_id = ats.channels[channel]
                if channel_id & self._channels == 0:
                    continue
                self._board.read(channel_id,             # Channel identifier
                           buffer.addr,           # Memory address of buffer
                           self._bytes_per_sample,        # Bytes per sample
                           record + 1,            # Record (1-indexed)
                           -self._pre_trigger_samples,    # Pre-trigger samples
                           self._samples_per_record)      # Samples per record
                bytesTransferred += self._bytes_per_record;

                # Records are arranged in the buffer as follows:
                # R0A, R1A, R2A ... RnA, R0B, R1B, R2B ...
                #
                # A 12-bit sample code is stored in the most significant bits of
                # in each 16-bit sample value.
                #
                # Sample codes are unsigned by default. As a result:
                # - 0x0000 represents a negative full scale input signal.
                # - 0x8000 represents a ~0V signal.
                # - 0xFFFF represents a positive full scale input signal.

                # Optionaly save data to file
                # if dataFile:
                #     buffer.buffer[:self._samples_per_record].tofile(dataFile)

                print(buffer.buffer[:self._samples_per_record])

                plt.plot(buffer.buffer[:self._samples_per_record])
                plt.ylabel('some numbers')
                plt.show()

                if ats.enter_pressed():
                    break

        # Compute the total transfer time, and display performance information.
        transferTime_sec = time.time() - start
        bytesPerSec = 0
        if transferTime_sec > 0:
            bytesPerSec = bytesTransferred / transferTime_sec
        print("Transferred %d bytes (%f bytes per sec)" %
              (bytesTransferred, bytesPerSec))

    def busy(self):
        '''
        Returns if the ats310 board is busy or not
        '''
        self._board.busy()


if __name__ == "__main__":
    # board = ats.Board(systemId = 1, boardId = 1)
    # ConfigureBoard(board)
    # AcquireData(board)

    my_ats310 = ATS310()
    my_ats310.start_capture()
    # my_ats310.start_capture()

    # my_ats310.prepare_acquisition()
    # my_ats310.start_capture()
