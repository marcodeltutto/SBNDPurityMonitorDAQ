from __future__ import division
import matplotlib.pyplot as plt
import ctypes
import numpy as np
import os
import signal
import sys
import time
import logging
import copy

try:
    from . import atsapi as ats
except:
    import atsapi as ats

# from sbndprmdaq.digitizer.board_wrapper import BoardWrapper

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
        super(ATS310Exception, self).__init__(self._message)

def get_digitizers():
    n_systems = ats.numOfSystems()
    n_boards = ats.boardsFound()

    boards_per_system = []
    for i in range(n_systems):
        boards_per_system.append(ats.boardsInSystemBySystemID(i+1))

    digitizers = []
    for i in range(n_systems):
        d = ATS310(systemId=i+1, boardId=1)
        digitizers.append(d)

    return digitizers


class ATS310():

    def __init__(self, systemId=1, boardId=1):
        '''
        Constructor
        '''
        self._logger = logging.getLogger(__name__)

        self._board = ats.Board(systemId, boardId)

        if self._board.handle is None or self._board.handle == 0:
            raise ATS310Exception(self._logger, 'Board handle is None or zero.')

        self._capture_success = False

        # self._board = BoardWrapper(self._board, ATS310Exception)

        self._samples_per_sec = 20000000.0
        self._samples_per_sec_id = ats.SAMPLE_RATE_20MSPS

        # TODO: Select the number of pre-trigger samples
        self._pre_trigger_samples = 512 #1024

        # TODO: Select the number of samples per record.
        self._post_trigger_samples = 10240 #1024

        # TODO: Select the number of records in the acquisition.
        self._records_per_capture = 10

        # TODO: Select the amount of time to wait for the acquisition to
        # complete to on-board memory.
        self._acquisition_timeout_sec = 30

        # TODO: Select the active channels.
        self._channels = ats.CHANNEL_A | ats.CHANNEL_B
        self._channel_count = 0
        for c in ats.channels:
            self._channel_count += (c & self._channels == c)

        self.configure_board()
        self.prepare_acquisition()

    def get_samples_per_second(self):
        return self._samples_per_sec

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

        self._board.setCaptureClock(ats.INTERNAL_CLOCK,
                                    self._samples_per_sec_id,
                                    ats.CLOCK_EDGE_RISING,
                                    0)

        # TODO: Select channel A input parameters as required.
        self._input_range_volts = 400.e-3 # volts
        self._board.inputControlEx(ats.CHANNEL_A,
                                   ats.DC_COUPLING,
                                   ats.INPUT_RANGE_PM_400_MV,
                                   # ats.INPUT_RANGE_PM_40_MV,
                                   # ats.IMPEDANCE_50_OHM)
                                   ats.IMPEDANCE_1M_OHM)

        # TODO: Select channel A bandwidth limit as required.
        self._board.setBWLimit(ats.CHANNEL_A, 0)


        # TODO: Select channel B input parameters as required.
        self._board.inputControlEx(ats.CHANNEL_B,
                                   ats.DC_COUPLING,
                                   ats.INPUT_RANGE_PM_400_MV,
                                   # ats.INPUT_RANGE_PM_40_MV,
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
                                        140, #200,
                                        ats.TRIG_ENGINE_K,
                                        ats.TRIG_DISABLE,
                                        ats.TRIGGER_SLOPE_POSITIVE,
                                        128)

        # TODO: Select external trigger parameters as required.
        # For a 1 V range, 0 is 0 V, 255 is 1 V
        # 0 is -1 V, 128 is 0 V, 255 is 1 V
        self._board.setExternalTrigger(ats.DC_COUPLING, ats.ETR_1V) #ats.ETR_TTL) # could be ETR_5V

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

        return True

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

        return True


    def start_capture(self):
        self._start = time.time() # Keep track of when acquisition started
        self._board.startCapture() # Start the acquisition
        print("Capturing %d record. Press <enter> to abort" % self._records_per_capture)

        return True


    def check_capture(self):
        self._capture_success = False
        while not ats.enter_pressed():
            if not self._board.busy():
                # Acquisition is done
                break
            if time.time() - self._start > self._acquisition_timeout_sec:
                self._board.abortCapture()
                self._logger.critical("Error: Capture timeout. Verify trigger")
                # raise ATS310Exception(self._logger, "Error: Capture timeout. Verify trigger")
                return
            time.sleep(10e-3)

        captureTime_sec = time.time() - self._start
        recordsPerSec = 0
        if captureTime_sec > 0:
            recordsPerSec = self._records_per_capture / captureTime_sec
        print("Captured %d records in %f rec (%f records/sec)" %
              (self._records_per_capture, captureTime_sec, recordsPerSec))
        self._capture_success = True

        return True


    def get_data(self):

        start = time.time() # Keep track of when acquisition started

        self._data = {
        'A': [],
        'B': []
        }

        if not self._capture_success:
            return self._data

        buffersCompleted = 0
        bytesTransferred = 0

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
                self._board.read(channel_id,                    # Channel identifier
                                 buffer.addr,                   # Memory address of buffer
                                 self._bytes_per_sample,        # Bytes per sample
                                 record + 1,                    # Record (1-indexed)
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

                if channel_id == ats.CHANNEL_A:
                    self._data['A'].append(copy.copy(buffer.buffer[:self._samples_per_record]))
                elif channel_id == ats.CHANNEL_B:
                    self._data['B'].append(copy.copy(buffer.buffer[:self._samples_per_record]))
                else:
                    raise ATS310Exception(self._logger, f'Unkown channel {channel_id}')

                print(channel_id, buffer.buffer[:self._samples_per_record])

                # plt.plot(buffer.buffer[:self._samples_per_record])
                # plt.ylabel('some numbers')
                # plt.show()

                if ats.enter_pressed():
                    break

        # Compute the total transfer time, and display performance information.
        transferTime_sec = time.time() - start
        bytesPerSec = 0
        if transferTime_sec > 0:
            bytesPerSec = bytesTransferred / transferTime_sec
        print("Transferred %d bytes (%f bytes per sec)" %
              (bytesTransferred, bytesPerSec))

        # self._convert_to_volts()

        print('Returning data, self._samples_per_record', self._samples_per_record)
        return self._data


    def _convert_to_volts(self):
        '''
        Converts self._data from ADC to volts
        '''

        bit_shift = int(4)
        bits_per_sample = int(12)
        code_zero = float(1 << (bits_per_sample - 1)) - 0.5
        code_range = float(1 << (bits_per_sample - 1)) - 0.5

        if self._data['A'] is not None:
            sample_code = np.right_shift(self._data['A'], bit_shift)
            self._data['A'] = self._input_range_volts * ((sample_code - code_zero) / code_range)

        if self._data['B'] is not None:
            sample_code = np.right_shift(self._data['B'], bit_shift)
            self._data['B'] = self._input_range_volts * ((sample_code - code_zero) / code_range)

        # sample_value = self._data['A'][0]
        # sample_code = sample_value >> bit_shift
        # sampleVolts = self._input_range_volts * (float(sample_code - code_zero) / code_range)
        # print('from', sample_value, 'to', sampleVolts)



    def busy(self):
        '''
        Returns if the ats310 board is busy or not
        '''
        return self._board.busy()


if __name__ == "__main__":
    # board = ats.Board(systemId = 1, boardId = 1)
    # ConfigureBoard(board)
    # AcquireData(board)

    digitizers = get_digitizers()

    my_ats310 = ATS310()
    my_ats310.start_capture()
    # my_ats310.start_capture()

    # my_ats310.prepare_acquisition()
    # my_ats310.start_capture()
