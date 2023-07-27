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


