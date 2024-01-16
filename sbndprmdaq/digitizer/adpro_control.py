'''
Contains class to control Analog Discovery Pro digitizer
'''
import logging
import time

import requests
import paramiko
from sshtunnel import SSHTunnelForwarder

from sbndprmdaq.digitizer.digitizer_base import DigitizerBase


class ADProControl(DigitizerBase):
    '''
    This class controls the Analog Discovery Pro digitizer
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_ids (list): List of PrM IDs (unused).
            config (dict): The configuration dictionary.
        '''

        self._logger = logging.getLogger(__name__)

        self._ssh_forward(config)
        self._start_api(config)

        self._to = 10 # timeout for requests


    def _ssh_forward(self, config):
        '''
        Open an SSH tunnel with the Analog Discovery Pro.

        Args:
            config (dict): The configuration dictionary.
        '''

        self._logger.info('Starting SSH forwarding for ADPro')

        self._server = SSHTunnelForwarder(config['adpro_ip'],
                                          ssh_username=config['adpro_username'],
                                          ssh_password=config['adpro_password'],
                                          remote_bind_address=('127.0.0.1', config['adpro_port']))

        self._server.start()

        self._url = 'http://127.0.0.1:' + str(self._server.local_bind_port)

        self._logger.info(f'ADPro API available at {self._url}')


    def _start_api(self, config):
        '''
        Starts the Analog Discovery Pro API on the ditizer itself.

        Args:
            config (dict): The configuration dictionary.
        '''

        self._logger.info('Starting API on ADPro')

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(config['adpro_ip'],
                          username=config['adpro_username'],
                          password=config['adpro_password'])

        command = 'cd adpro_api '
        command += '/home/digilent/.local/bin/uvicorn main:app --reload'
        stdin, stdout, stderr = self._ssh.exec_command(command)
        self._logger.info('Executed ' + command + ' on ' + config['adpro_ip'])


    def busy(self):

        return requests.get(self._url + "/digitizer/busy", timeout=self._to).json()['busy']


    def get_trigger_sample(self):

        return requests.get(self._url + "/digitizer/trigger_sample", timeout=self._to).json()['trigger_sample']


    def get_samples_per_second(self):

        return requests.get(self._url + "/digitizer/samples_per_second", timeout=self._to).json()['samples_per_second']

    def set_samples_per_second(self):

        return requests.get(self._url + "/digitizer/set_samples_per_second", timeout=self._to).json()['set_samples_per_second']


    def get_number_acquisitions(self):

        return requests.get(self._url + "/digitizer/number_acquisitions", timeout=self._to).json()['number_acquisitions']


    def set_number_acquisitions(self, n):

        return requests.get(self._url + "/digitizer/set_number_acquisitions", timeout=self._to).json()['set_number_acquisitions']


    def get_pre_trigger_samples(self):

        return requests.get(self._url + "/digitizer/pre_trigger_samples", timeout=self._to).json()['pre_trigger_samples']


    def get_post_trigger_samples(self):

        return requests.get(self._url + "/digitizer/post_trigger_samples", timeout=self._to).json()['post_trigger_samples']


    def get_input_range_volts(self):

        return requests.get(self._url + "/digitizer/input_range_volts", timeout=self._to).json()['input_range_volts']


    def lamp_on(self):

        response = requests.get(self._url + "/lamp_control/on", timeout=self._to)

        if response.json()['status'] != 'on':
            self._logger.critical('API error: cannot turn lamp on')


    def lamp_off(self):

        response = requests.get(self._url + "/lamp_control/off", timeout=self._to)

        if response.json()['status'] != 'off':
            self._logger.critical('API error: cannot turn lamp off')


    def lamp_frequency(self, freq):

        response = requests.get(self._url + f"/lamp_frequency/{freq}", timeout=self._to)

        if int(response.json()['frequency']) != freq:
            self._logger.critical(f'API error: cannot set frequency to {freq}')


    def start_capture(self):

        self._logger.info('Starting capture')

        response = requests.get(self._url + "/digitizer/start_capture", timeout=self._to)

        print(response.json()['status'])
        if not response.json()['status']:
            self._logger.critical('API error: start_capture failed')

        return response.json()['status']


    def check_capture(self):

        start = time.time()
        while 10 > time.time() - start:
            response = requests.get(self._url + "/digitizer/check_capture", timeout=self._to)
            if response.json()['status']:
                return True

        return False


    def get_data(self):

        response = requests.get(self._url + "/digitizer/get_data", timeout=self._to)

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


if __name__ == "__main__":
    adpro = ADProControl()

