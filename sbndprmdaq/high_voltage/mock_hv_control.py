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
        self._hv_status = {}
        for prm_id in self._prm_ids:
            self._hvs[prm_id] = {
                'anode': 5000,
                'cathode': -50,
                'anodegrid': 1000
            }
            self._hv_status[prm_id] = {
                'anode': False,
                'cathode': False,
                'anodegrid': False
            }

    def is_crate_on(self, ip):
        '''
        Returns True if the crate is ON
        '''
        return True

    def hv_on(self, prm_id=1):
        '''
        Sets the HV ON.
        '''
        self._logger.info('HV ON.')
        self._hv_status[prm_id] = {
            'anode': True,
            'cathode': True,
            'anodegrid': True
        }

    def hv_off(self, prm_id=1):
        '''
        Sets the OFF
        '''
        self._logger.info('HV OFF.')
        self._hv_status[prm_id] = {
            'anode': False,
            'cathode': False,
            'anodegrid': False
        }

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

    def get_hv_value(self, item, prm_id=1):
        '''
        Returns the HV set values

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
        '''
        return self._hvs[prm_id][item]

    def get_hv_sense_value(self, item, property='voltage', prm_id=1):
        '''
        Returns the HV sensed values

        Args:
            item: 'anode', 'anodegrid', or 'cathode'
            property: 'voltage' only
            prm_id: the prm id
        '''
        return self._hvs[prm_id][item]

    def get_hv_status(self, item, prm_id=1):
        '''
        Returns wheter the HV is on or off

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
            prm_id: the prm id
        '''
        return self._hv_status[prm_id][item]
