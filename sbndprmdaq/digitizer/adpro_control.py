import logging
import time
import requests

class ADProControl():

    def __init__(self, prm_ids=None, config=None):

        self._logger = logging.getLogger(__name__)

        self._url = "http://localhost:8000"

    def busy(self):
        # TODO
        return False

    def get_trigger_sample(self):
        # TODO
        return 1000

    def get_samples_per_second(self):
        # TODO
        return 2000000.0

    def get_number_acquisitions(self):
        # TODO
        return 0

    def get_pre_trigger_samples(self):
        # TODO
        return 0

    def get_post_trigger_samples(self):
        # TODO
        return 0

    def get_input_range_volts(self):
        # TODO
        return 0

    def lamp_on(self):

        response = requests.get(self._url + "/lamp_control/on")

        if response.json()['status'] != 'on':
            self._logger.critical('API error: cannot turn lamp on')


    def lamp_off(self):

        response = requests.get(self._url + "/lamp_control/off")

        if response.json()['status'] != 'off':
            self._logger.critical('API error: cannot turn lamp off')


    def start_capture(self):

        self._logger.info('Starting capture')

        response = requests.get(self._url + "/digitizer/start_capture")

        print(response.json()['status'])
        if response.json()['status'] != True:
            self._logger.critical('API error: start_capture failed')

        return response.json()['status']


    def check_capture(self):

        start = time.time()
        status = False
        while 10 > time.time() - start:
            response = requests.get(self._url + "/digitizer/check_capture")
            if response.json()['status']:
                return True

        return False


    def get_data(self):

        response = requests.get(self._url + "/digitizer/get_data")

        # if response.json()['data'] != 'true':
        #     self._logger.critical('API error: start_capture failed')

        data = response.json()['data']

        # Rename 1->A 2->B, and embed list into another list
        # data['A'] = [data[1]]
        # data['B'] = [data[2]]
        # data['A'] = [data[1]]
        # data['B'] = [data[2]]
        # del data[1]
        # del data[2]

        return data




