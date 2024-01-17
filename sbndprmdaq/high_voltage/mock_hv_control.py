'''
Contains a mock class for testing purposes
'''

from .hv_control_base import HVControlBase

class MockHVControl(HVControlBase):
    '''
    A mock class HV control class for testing purposes
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        super().__init__(prm_ids=prm_ids, config=config)

        self._logger.info('MockHVControl created.')

        self._prm_ids = prm_ids
        self._hvs = {}
        for prm_id in self._prm_ids:
            self._hvs[prm_id] = {
                'anode': 0,
                'cathode': 0,
                'anodegrid': 0
            }

    def is_crate_on(self):
        '''
        Returns True if the crate is ON
        '''

        return True


    def hv_on(self, prm_id=1):
        '''
        Sets the HV ON.
        '''
        self._logger.info('HV ON.')


    def hv_off(self, prm_id=1):
        '''
        Sets the OFF
        '''
        self._logger.info('HV OFF.')


    def set_hv_value(self, item, value, prm_id=1):
        '''
        Sets HV value

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
            value: the HV value
        '''
        self._hvs[prm_id][item] = value
        self._logger.info('HV value set.')


    def get_hv_value(self, item, prm_id):
        '''
        Returns the HV set values

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
        '''
        return self._hvs[prm_id][item]


    def get_hv_sense_value(self, item, prm_id):
        '''
        Returns the HV sensed values

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
        '''
        return self._hvs[prm_id][item]

    def get_hv_status(self, item, prm_id):
        '''
        Returns wheter the HV is on or off

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
        '''
        return self._hvs[prm_id][item] != 0
