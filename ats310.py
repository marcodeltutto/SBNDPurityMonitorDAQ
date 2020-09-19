import ctypes
import os
import time
import atsapi as ats

class ATS310Exception(Exception):
    """
    Exception class for ATS310.
    """

    def __init__(self, message):
        '''
        Contructor
        '''
        self._message
        super(ESP32Exception, self).__init__(self._message)

class ATS310():

    def __init__(self):
        '''
        Constructor
        '''
        self._board = ats.Board(systemId = 1, boardId = 1)

        if self._board.handle is None or self._board.handle == 0:
            raise ESP32Exception('Board handle is None or zero.')

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

        self._data = {ats.CHANNEL_A: [], ats.CHANNEL_B: []}

        self._calculate_bytes()

        self._configure_board()


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
        samplesPerSec = 20000000.0
        print('=======',self._board)
        print('======= handle',self._board.handle)
        self._board.setCaptureClock(ats.INTERNAL_CLOCK,
                                    ats.SAMPLE_RATE_20MSPS,
                                    ats.CLOCK_EDGE_RISING,
                                    0)

        # TODO: Select channel A input parameters as required.
        self._board.inputControlEx(ats.CHANNEL_A,
                                   ats.DC_COUPLING,
                                   ats.INPUT_RANGE_PM_400_MV,
                                   ats.IMPEDANCE_50_OHM)

        # TODO: Select channel A bandwidth limit as required.
        self._board.setBWLimit(ats.CHANNEL_A, 0)


        # TODO: Select channel B input parameters as required.
        self._board.inputControlEx(ats.CHANNEL_B,
                                   ats.DC_COUPLING,
                                   ats.INPUT_RANGE_PM_400_MV,
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
        self._board.configureAuxIO(ats.AUX_OUT_TRIGGER,
                                   0)

        # Set the record size
        self._board.setRecordSize(self._pre_trigger_samples, self._post_trigger_samples)

        # Configure the number of records in the acquisition
        self._board.setRecordCount(self._records_per_capture)

        self._channel_count = 0
        for c in ats.channels:
            self._channel_count += (c & self._channels == c)


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
        '''

        self._start_time = time.time()

        self._board.startCapture() # Start the acquisition

        # while not ats.enter_pressed():
        #     if not board.busy():
        #         # Acquisition is done
        #         break
        #     if time.time() - start > acquisition_timeout_sec:
        #         board.abortCapture()
        #         raise Exception("Error: Capture timeout. Verify trigger")
        #     time.sleep(10e-3)

        # captureTime_sec = time.time() - start


    def abort_capture(self):
        '''
        Abort an acquisition to on-board memory.
        '''
        self._board.abortCapture()

        print('Data captured for seconds:', time.time() - self._start_time)


    def busy(self):
        '''
        Returns true if the board is busy
        '''

        return self._board.busy


    def get_data(self):
        '''
        Gets the data from the ATS onboard memory and returns
        it in a dictionary (one entry per channel)

        Returns:
        - a dictionaty with the data per channel
        '''

        start = time.time()

        sample_type = ctypes.c_uint8
        self._buffer = ats.DMABuffer(self._board.handle, sample_type, self._bytes_per_buffer + 16)

        bytes_transferred = 0

        for d in self._data.values():
            d = []

        for record in range(self._records_per_capture):

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
                self._data[ch_name].append(self._buffer.buffer[:self._samples_per_record])

        print('Data read from ATS onboard memory in', time.time() - start, 'seconds.')
        print('Bytes transferred:', bytes_transferred)

        return self._data


# def AcquireData(board):
    # # TODO: Select the number of pre-trigger samples
    # preTriggerSamples = 1024

    # # TODO: Select the number of samples per record.
    # postTriggerSamples = 1024

    # # TODO: Select the number of records in the acquisition.
    # recordsPerCapture = 100

    # # TODO: Select the amount of time to wait for the acquisition to
    # # complete to on-board memory.
    # acquisition_timeout_sec = 10

    # # TODO: Select the active channels.
    # channels = ats.CHANNEL_A | ats.CHANNEL_B
    # channelCount = 0
    # for c in ats.channels:
    #     channelCount += (c & channels == c)

    # # TODO: Should data be saved to file?
    # saveData = False
    # dataFile = None
    # if saveData:
    #     dataFile = open(os.path.join(os.path.dirname(__file__),
    #                                  "data.bin"), 'wb')

    # # Compute the number of bytes per record and per buffer
    # memorySize_samples, bitsPerSample = board.getChannelInfo()
    # bytesPerSample = (bitsPerSample.value + 7) // 8
    # samplesPerRecord = preTriggerSamples + postTriggerSamples
    # bytesPerRecord = bytesPerSample * samplesPerRecord

    # # Calculate the size of a record buffer in bytes. Note that the
    # # buffer must be at least 16 bytes larger than the transfer size.
    # bytesPerBuffer = (bytesPerSample *
    #                   (samplesPerRecord + 0))

    # # Set the record size
    # board.setRecordSize(preTriggerSamples, postTriggerSamples)

    # # Configure the number of records in the acquisition
    # board.setRecordCount(recordsPerCapture)

    # start = time.time() # Keep track of when acquisition started
    # board.startCapture() # Start the acquisition
    # print("Capturing %d record. Press <enter> to abort" % recordsPerCapture)
    # buffersCompleted = 0
    # bytesTransferred = 0
    # while not ats.enter_pressed():
    #     if not board.busy():
    #         # Acquisition is done
    #         break
    #     if time.time() - start > acquisition_timeout_sec:
    #         board.abortCapture()
    #         raise Exception("Error: Capture timeout. Verify trigger")
    #     time.sleep(10e-3)

    # captureTime_sec = time.time() - start
    # recordsPerSec = 0
    # if captureTime_sec > 0:
    #     recordsPerSec = recordsPerCapture / captureTime_sec
    # print("Captured %d records in %f rec (%f records/sec)" %
    #       (recordsPerCapture, captureTime_sec, recordsPerSec))

    # sample_type = ctypes.c_uint8
    # if bytesPerSample > 1:
    #     sample_type = ctypes.c_uint16

    # buffer = ats.DMABuffer(board.handle, sample_type, bytesPerBuffer + 16)

    # # Transfer the records from on-board memory to our buffer
    # print("Transferring %d records..." % recordsPerCapture)

    # for record in range(recordsPerCapture):
    #     if ats.enter_pressed():
    #         break
    #     for channel in range(channelCount):
    #         channelId = ats.channels[channel]
    #         if channelId & channels == 0:
    #             continue
    #         board.read(channelId,             # Channel identifier
    #                    buffer.addr,           # Memory address of buffer
    #                    bytesPerSample,        # Bytes per sample
    #                    record + 1,            # Record (1-indexed)
    #                    -preTriggerSamples,    # Pre-trigger samples
    #                    samplesPerRecord)      # Samples per record
    #         bytesTransferred += bytesPerRecord;

    #         # Records are arranged in the buffer as follows:
    #         # R0A, R1A, R2A ... RnA, R0B, R1B, R2B ...
    #         #
    #         # A 12-bit sample code is stored in the most significant bits of
    #         # in each 16-bit sample value.
    #         #
    #         # Sample codes are unsigned by default. As a result:
    #         # - 0x0000 represents a negative full scale input signal.
    #         # - 0x8000 represents a ~0V signal.
    #         # - 0xFFFF represents a positive full scale input signal.

    #         # Optionaly save data to file
    #         if dataFile:
    #             buffer.buffer[:samplesPerRecord].tofile(dataFile)

    #         if ats.enter_pressed():
    #             break

    # # Compute the total transfer time, and display performance information.
    # transferTime_sec = time.time() - start
    # bytesPerSec = 0
    # if transferTime_sec > 0:
    #     bytesPerSec = bytesTransferred / transferTime_sec
    # print("Transferred %d bytes (%f bytes per sec)" %
    #       (bytesTransferred, bytesPerSec))

if __name__ == "__main__":
    my_ats310 = ATS310()
    my_ats310.acquire_data()

    while True:
        if not my_ats310.busy():
            # Acquisition is done
            break
        time.sleep(10e-3)

    data = my_ats310.get_data()
    print(data)
