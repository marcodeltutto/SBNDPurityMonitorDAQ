from .hv_control_base import *

class MockHVControl(HVControlBase):
    '''
    Controls the HV via the MPODmini.
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        super(MockHVControl, self).__init__(prm_ids=prm_ids, config=config)

        self._logger.info('MockHVControl created.')




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

        return


    def hv_off(self, prm_id=1):
        '''
        Sets the OFF
        '''
        self._logger.info('HV OFF.')

        return


    def set_hv_value(self, posneg, value, prm_id=1):
        '''
        Sets HV value

        args:
        posneg: 'pos' or 'neg'
        '''
        self._logger.info('HV value set.')

        return


    def get_hv_value(self, posneg, prm_id):
        '''
        Returns the HV set values

        args:
        posneg: 'pos' or 'neg'
        prm_id: the prm id
        '''

        return 9999

    def get_hv_sense_value(self, posneg, prm_id):
        '''
        Returns the HV sensed values

        args:
        posneg: 'pos' or 'neg'
        prm_id: the prm id
        '''

        return 9999

    def get_hv_status(self, posneg, prm_id):
        '''
        Returns wheter the HV is on or off

        args:
        posneg: 'pos' or 'neg'
        prm_id: the prm id
        '''
        return True



