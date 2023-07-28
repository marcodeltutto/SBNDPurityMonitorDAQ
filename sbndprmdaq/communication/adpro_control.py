import logging
import requests

class ADProControl():

    def __init__(self, prm_ids=None, config=None):

        self._logger = logging.getLogger(__name__)

        self._url = "http://localhost:8000"

    def lamp_on(self, prm_id=1):

        response = requests.get(self._url + "/lamp_control/on")

        if response.json()['status'] != 'on':
            self._logger.critical('API error: cannot turn lamp on')


    def lamp_off(self, prm_id=1):

        response = requests.get(self._url + "/lamp_control/off")

        if response.json()['status'] != 'off':
            self._logger.critical('API error: cannot turn lamp off')


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

        print(type(response.json()['data']))
        print((response.json()['data']))
        return

        # return response.json()['status']



