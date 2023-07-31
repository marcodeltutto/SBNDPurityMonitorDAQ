
import logging
from ats310 import get_digitizers, ATS310Exception
# from adpro_control import get_adpro_digitizers, ADProControl

class PrMDigitizer():

    def __init__(self, prm_ids=None, config=None):

        self._logger = logging.getLogger(__name__)
        self._digitizers = {}

        print('prm_id_to_ats_systemid', config['prm_id_to_ats_systemid'])
        print('prm_id_to_adpro_channels', config['prm_id_to_adpro_channels'])
        print('prm_id_to_digitizer_type', config['prm_id_to_digitizer_type'])

        for prm_id, digitizer_type in config['prm_id_to_digitizer_type'].items():
            self._logger(f"Setting up PrM {prm_id} with digitizer {digitizer_type}.")
            if digitizer_type == 'adpro':
                digitizer = get_adpro_digitizer(channels=config['prm_id_to_adpro_channels'][prm_id])
            elif digitizer_type == 'ats310':
                digitizer = get_ads310_digitizer(channels=config['prm_id_to_ats_systemid'][prm_id])
            else:
                self._logger.critical('Digitizer option not recognized: {digitizer_type}.')

            if digitizer is None:
                if self._window is not None:
                    self._window.missing_digitizer(prm_id)
                    self._digitizers[prm_id] = None
                continue

            self._digitizers[prm_id] = digitizer




    def start_capture(self, prm_id):

        response = requests.get(self._url + "/digitizer/start_capture")

        if response.json()['status'] != 'true':
            self._logger.critical('API error: start_capture failed')

        return response.json()['status']


    def check_capture(self, prm_id):

        response = requests.get(self._url + "/digitizer/check_capture")

        # if response.json()['status'] != 'true':
        #     self._logger.critical('API error: start_capture failed')

        return response.json()['status']


    def get_data(self, prm_id):

        response = requests.get(self._url + "/digitizer/get_data")

        # if response.json()['data'] != 'true':
        #     self._logger.critical('API error: start_capture failed')

        return response.json()['data']

        # return response.json()['status']