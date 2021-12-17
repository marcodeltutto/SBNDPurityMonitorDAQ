from .hv_control_base import *
import subprocess
import time

class HVControlMPOD(HVControlBase):
    '''
    Controls the HV via the MPODmini.
    '''

    def __init__(self, prm_ids=None, config=None):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        super(HVControlMPOD, self).__init__(prm_ids=prm_ids, config=config)

        #
        # Setting IP MPOD address
        #
        if 'mpod_ip' not in config:
        	raise HVControlException(self._logger, 'Missing mpod_ip in config.')

        self._mpod_ip = config['mpod_ip']

        #
        # Setting HV channels
        #
        self._channels = {}
        for prm_id in prm_ids:
            if f'mpod_prm{prm_id}_ch' not in config:
                raise HVControlException(self._logger,
                                         f'Missing mpod_prm{prm_id}_ch in config.')
            else:
                self._channels[prm_id] = config[f'mpod_prm{prm_id}_ch']

        self._logger.info('HVControlMPOD created.')

    def _set_cmd(self, name='sysMainSwitch.', ch='0', t='i', value='0'):
        cmd = "snmpset -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c private "
        cmd += self._mpod_ip + ' '
        cmd += name
        cmd += ch + ' '
        cmd += t + ' '
        cmd += value
        self._logger.info('Subprocess: ' + cmd)
        # subprocess.run(cmd.split())

        # Start a subprocess
        start = time.time()
        proc = subprocess.Popen(cmd.split())
        while proc.poll():
            time.sleep(0.1)
            if time.time() - start > 5:
                proc.terminate()
                raise HVControlException(self._logger,
                                         'Timeout during command: ' + cmd)

        # cmd = "snmpset -v 2c -M /usr/share/snmp/mibs/  -m +WIENER-CRATE-MIB -c private 192.168.0.25  sysMainSwitch.0 i 1".format()


    def hv_on(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the HV ON.
        '''
        channel = self._channels[prm_id]
        self._set_cmd(name='outputSwitch.u', ch=str(channel), t='i', value='1')
        return


    def hv_off(self, prm_id=1):
        '''
        Sets the parallel port pin that turns the HV OFF
        '''
        channel = self._channels[prm_id]
        self._set_cmd(name='outputSwitch.u', ch=str(channel), t='i', value='0')
        return


    def set_hv_value(self):
        return
