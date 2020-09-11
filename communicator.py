# import pyfirmata
# import time

# class Communicator():

#     def __init__(self, port):

#         self._board = pyfirmata.Arduino(port)

#     def start_prm(self):
#         self._board.digital[8].write(1)

#     def stop_prm(self):
#         self._board.digital[8].write(0)

from psychopy import parallel

class Communicator():

    def __init__(self, port=0x0):

        self._port = parallel.ParallelPort(address=port)
        self._port.setData(0)

    def start_prm(self):
        self._port.setPin(2, 1)

    def stop_prm(self):
        self._port.setPin(2, 0)