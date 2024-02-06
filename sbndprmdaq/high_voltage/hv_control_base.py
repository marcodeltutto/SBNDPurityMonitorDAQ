'''
Contains base class for HV control
'''
import logging
from abc import ABC, abstractmethod

import time
import numpy as np

class HVControlException(Exception):
    '''
    Exception class for ATS310.
    '''

    def __init__(self, logger, message):
        '''
        Contructor.

        Args:
            logger (PrMLogger): The logger widget.
            message (str): The error message.
        '''
        self._message = message
        logger.critical(self._message)
        super().__init__(self._message)


#pylint: disable=invalid-name
class HVControlBase(ABC):
    '''
    A base class to control the HV.
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''

        self._logger = logging.getLogger(__name__)

        if prm_ids is None:
            raise HVControlException(self._logger,
                'Need to set prm_ids.')

        self._config = config

        self._logger.info('HVControl created.')

    @abstractmethod
    def is_crate_on(self, ip):
        '''
        Returns True if the crate is ON
        '''

    @abstractmethod
    def hv_on(self, prm_id=1):
        '''
        Turn the HV ON.
        '''

    @abstractmethod
    def hv_off(self, prm_id=1):
        '''
        Turn the HV OFF.
        '''

    @abstractmethod
    def get_hv_value(self, item, prm_id=1):
        '''
        Returns the HV set values

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
        '''

    @abstractmethod
    def get_hv_sense_value(self, item, prm_id=1):
        '''
            Returns the HV sensed values

            args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
        '''

    @abstractmethod
    def get_hv_status(self, item, prm_id=1):
        '''
        Returns wheter the HV is on or off

        args:
        item: 'anode', 'anodegrid', or 'cathode',
        prm_id: the prm id
        '''

    #pylint: disable=unused-variable
    def hv_stable(self, prm_id=1, n_measurements=10):
        '''
        Returns true is HV is stable
        '''
        self._logger.info(f'Waiting for HV to stabilize for PrM {prm_id}...')
        status = 0

        for item in ['cathode', 'anodegrid', 'anode']:
            measurements = []
            for meas in range(n_measurements):
                hv = self.get_hv_sense_value(item, prm_id)
                measurements.append(hv)
                time.sleep(0.2)

            # print('prm_id, ', prm_id, 'item', item, 'RMS: ', np.std(measurements))

            if np.std(measurements) < 0.5:
                status = status + 1

        if status == 3:
            return True
            self._logger.info(f'...HV is stabile for PrM {prm_id}.')

        self._logger.info(f'...cannot stabilize HV for PrM {prm_id}.')

        return False



    def check_hv_range(self, prm_id=1):
        '''
        Checks if the HV is whitin a range
        '''
        bad = []
        for item in ['cathode', 'anodegrid', 'anode']:
            hv_range = self._config["prm_hv_ranges"][prm_id][item]
            if not hv_range[0] <= self.get_hv_sense_value(item, prm_id) <= hv_range[1]:
                bad.append(item)

        if len(bad) == 0:
            return 0

        return bad
