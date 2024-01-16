'''
The purity monitor mock manager (for testing).
'''

from .manager import PrMManager
from sbndprmdaq.communication.mock_hv_control import MockHVControl
from sbndprmdaq.digitizer.mock_prm_digitizer import MockPrMDigitizer

class MockPrMManager(PrMManager):
    '''
    A PrM manager to be used for testing purposes
    '''

    def _set_digitizer_and_hv(self, config):

        self._prm_digitizer = MockPrMDigitizer(config)
        self._hv_control = MockHVControl(config['prm_ids'], config=config)

    def retrieve_run_numbers(self):
        self._run_numbers[1] = 100
        self._run_numbers[2] = 200
        self._run_numbers[3] = 300

    def write_run_numbers(self):
        pass

    def heartbeat(self):
        pass

    def exit(self):
        pass
