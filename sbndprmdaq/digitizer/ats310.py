import matplotlib.pyplot as plt
import numpy as np
import ctypes
import os
import time
try:
    from . import atsapi as ats
except:
    import atsapi as ats
import logging

samplesPerSec = None

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

        # TODO: Select the number of pre-trigger samples
        self._pre_trigger_samples = 1024

        # TODO: Select the number of samples per record.
        self._post_trigger_samples = 1024

        # TODO: Select the number of records in the acquisition.
        self._records_per_capture = 100

        # TODO: Select the amount of time to wait for the acquisition to
        # complete to on-board memory.
        self._acquisition_timeout_sec = 10

        # TODO: Select the active channels.
        self._channels = ats.CHANNEL_A | ats.CHANNEL_B

        self._channel_map = {ats.CHANNEL_A: 'A', ats.CHANNEL_B: 'B'}

        # self._data = {ats.CHANNEL_A: [], ats.CHANNEL_B: []}
        self._data = {'A': [], 'B': []}


        self._configure_board()
        self._calculate_bytes()


    def __del__(self):
        '''
        Destructor
        '''
        del self._board


    def _configure_board(self):
        '''
        Configures the board
        '''
        # TODO: Select clock parameters as required to generate this
        # sample rate
        #
        # For example: if samplesPerSec is 100e6 (100 MS/s), then you can
        # either:
        #  - select clock source INTERNAL_CLOCK and sample rate
        #    SAMPLE_RATE_100MSPS
        #  - or select clock source FAST_EXTERNAL_CLOCK, sample rate
        #    SAMPLE_RATE_USER_DEF, and connect a 100MHz signal to the
        #    EXT CLK BNC connector
        global samplesPerSec
        samplesPerSec = 20000000.0

        self._board.setCaptureClock(ats.INTERNAL_CLOCK,
                                    ats.SAMPLE_RATE_20MSPS,
                                    ats.CLOCK_EDGE_RISING,
                                    0)

        # TODO: Select channel A input parameters as required.
        self._board.inputControlEx(ats.CHANNEL_A,
                                   ats.DC_COUPLING,
                                   ats.INPUT_RANGE_PM_400_MV,
                                   # ats.INPUT_RANGE_PM_4_V,
                                   ats.IMPEDANCE_50_OHM)

        # TODO: Select channel A bandwidth limit as required.
        self._board.setBWLimit(ats.CHANNEL_A, 0)


        # TODO: Select channel B input parameters as required.
        self._board.inputControlEx(ats.CHANNEL_B,
                                   ats.DC_COUPLING,
                                   ats.INPUT_RANGE_PM_400_MV,
                                   # ats.INPUT_RANGE_PM_4_V,
                                   ats.IMPEDANCE_50_OHM)

        # TODO: Select channel B bandwidth limit as required.
        self._board.setBWLimit(ats.CHANNEL_B, 0)

        # TODO: Select trigger inputs and levels as required.
        self._board.setTriggerOperation(ats.TRIG_ENGINE_OP_J,
                                        ats.TRIG_ENGINE_J,
                                        ats.TRIG_CHAN_A,
                                        ats.TRIGGER_SLOPE_POSITIVE,
                                        150,
                                        ats.TRIG_ENGINE_K,
                                        ats.TRIG_DISABLE,
                                        ats.TRIGGER_SLOPE_POSITIVE,
                                        128)

        # TODO: Select external trigger parameters as required.
        self._board.setExternalTrigger(ats.DC_COUPLING,
                                       ats.ETR_TTL)

        # TODO: Set trigger delay as required.
        triggerDelay_sec = 0
        triggerDelay_samples = int(triggerDelay_sec * samplesPerSec + 0.5)
        self._board.setTriggerDelay(triggerDelay_samples)

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

        # Set the record size
        self._board.setRecordSize(self._pre_trigger_samples, self._post_trigger_samples)

        # Configure the number of records in the acquisition
        self._board.setRecordCount(self._records_per_capture)

        self._channel_count = 0
        for c in ats.channels:
            self._channel_count += (c & self._channels == c)

        self._logger.critical('ATS board configured.')


    def _calculate_bytes(self):
        '''
        Calculates the bytes per record and per buffer
        '''

        # Compute the number of bytes per record and per buffer
        memory_size_samples, bits_per_sample = self._board.getChannelInfo()
        self._bytes_per_sample = (bits_per_sample.value + 7) // 8
        self._samples_per_record = self._pre_trigger_samples + self._post_trigger_samples
        self._bytes_per_record = self._bytes_per_sample * self._samples_per_record

        # Calculate the size of a record buffer in bytes. Note that the
        # buffer must be at least 16 bytes larger than the transfer size.
        self._bytes_per_buffer = (self._bytes_per_sample * (self._samples_per_record + 0))


    def acquire_data(self):
        '''
        Starts the acquisition
        '''

        self._start_time = time.time()

        self._board.startCapture()

        self._logger.critical('Data acquisition started.')


    def abort_capture(self):
        '''
        Abort an acquisition to on-board memory.
        '''
        self._board.abortCapture()

        self._logger.critical(f'Data captured for seconds: {time.time() - self._start_time}')


    def busy(self):
        '''
        Returns true if the board is busy
        '''

        return self._board.busy()


    def get_data(self):
        '''
        Gets the data from the ATS onboard memory and returns
        it in a dictionary (one entry per channel)

        Returns:
        - a dictionaty with the data per channel
        '''

        self._logger.critical('Prepare to read the data.')

        start = time.time()

        sample_type = ctypes.c_uint8
        self._buffer = ats.DMABuffer(self._board.handle, sample_type, self._bytes_per_buffer + 16)

        bytes_transferred = 0

        for d in self._data.values():
            d = []

        for record in range(self._records_per_capture):

            self._logger.critical(f'Reading record {record}/{self._records_per_capture}.')

            for channel in range(self._channel_count):

                channel_id = ats.channels[channel]
                if channel_id & self._channels == 0:
                    continue

                self._board.read(channel_id,                    # Channel identifier
                                 self._buffer.addr,             # Memory address of buffer
                                 self._bytes_per_sample,        # Bytes per sample
                                 record + 1,                    # Record (1-indexed)
                                 -self._pre_trigger_samples,    # Pre-trigger samples
                                 self._samples_per_record)      # Samples per record

                bytes_transferred += self._bytes_per_record;

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

                ch_name = self._channel_map[channel_id]
                print('ch_name', ch_name)
                self._data[ch_name].append(self._buffer.buffer[:self._samples_per_record])
                plt.plot(self._buffer.buffer[:self._samples_per_record])
                plt.ylabel('some numbers')
                plt.show()

        self._logger.critical(f'Data read from ATS onboard memory in {time.time() - start} seconds.')
        self._logger.critical(f'DBytes transferred: {bytes_transferred}.')

        return self._data


    def set_pre_trigger_samples(self, pre_trigger_samples):
        '''
        Sets the number of pre-trigger samples
        '''
        self._pre_trigger_samples = pre_trigger_samples

    def set_post_trigger_samples(self, post_trigger_samples):
        '''
        Sets the number of samples per record.
        '''
        self._post_trigger_samples = post_trigger_samples

    def set_records_per_capture(self, records_per_capture):
        '''
        Sets the number of records in the acquisition.
        '''
        self._records_per_capture = records_per_capture




if __name__ == "__main__":
    my_ats310 = ATS310()
    # my_ats310._board.setTriggerTimeOut(2)
    my_ats310.set_records_per_capture(1)
    my_ats310.set_post_trigger_samples(50000)
    my_ats310.acquire_data()

    while not my_ats310.busy():
        time.sleep(10e-3)

    data = my_ats310.get_data()
    data = data['A'][0]
    # plt.plot(np.arange(len(data)), data)
    # plt.ylabel('some numbers')
    # plt.show()
