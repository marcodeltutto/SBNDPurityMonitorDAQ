from .hv_control_base import *

from puresnmp import set

class HVControlMPOD(HVControlBase):
    '''
    Controls the HV via the MPODmini.
    '''

    def __init__(self, prm_id=1, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        super(HVControlMPOD, self).__init__(prm_id=prm_id, config=config)

        if 'mpod_ip' not in config:
        	raise HVControlException(self._logger, 'Missing mpod_ip in config.')

        self._logger.info('HVControlMPOD created.')

    def hv_on(self):
        '''
        Sets the parallel port pin that turns the HV ON.
        '''
        set('on')
        return


    def hv_off(self):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        set('off')
        return
