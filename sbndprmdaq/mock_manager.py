'''
The purity monitor mock manager (for testing).
'''

from sbndprmdaq.high_voltage.mock_hv_control import MockHVControl
from sbndprmdaq.digitizer.mock_prm_digitizer import MockPrMDigitizer
from .manager import PrMManager

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

    #pylint: disable=duplicate-code
    def _thread_data(self, data):
        '''
        Remove output_to_epics call for testing
        '''
        self._logger.info(f'Got data for PrM {data["prm_id"]}.')

        if data['status']:
            self._data[data['prm_id']] = {
                'A': data['A'],
                'B': data['B'],
                'time': data['time'],
            }
            self.save_data(data['prm_id'])
            self._logger.info(f'Saved data for PrM {data["prm_id"]}.')
        else:
            self._logger.info(f'Bad capture, no data to save for PrM {data["prm_id"]}.')
