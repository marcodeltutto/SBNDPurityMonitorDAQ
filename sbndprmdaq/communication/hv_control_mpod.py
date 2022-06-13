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

        # Check if the HV crate is on or off
        self._logger.info('HV Crate is on? {status}'.format(status=self.is_crate_on()))

        if not self.is_crate_on():
            # Turn crate on
            self._logger.info('Turning crate on. Wait for 10 seconds...')
            self._set_cmd(name='sysMainSwitch.', ch=str(0), t='i', value='1')
            time.sleep(10)
            self._logger.info('...done.')

        #
        # Setting HV channels
        #
        self._positive_channels = {}
        self._negative_channels = {}
        for prm_id in prm_ids:
            if f'mpod_prm{prm_id}_positive_ch' not in config or f'mpod_prm{prm_id}_negative_ch' not in config:
                raise HVControlException(self._logger,
                                         f'Missing mpod_prm{prm_id}_positive_ch or mpod_prm{prm_id}_negative_ch in config.')
            else:
                self._positive_channels[prm_id] = config[f'mpod_prm{prm_id}_positive_ch']
                self._negative_channels[prm_id] = config[f'mpod_prm{prm_id}_negative_ch']

                # self.set_hv_value(0, prm_id)

        self._logger.info('HVControlMPOD created.')

    def _set_cmd(self, name='sysMainSwitch.', ch='0', t='i', value='0'):
        cmd = "snmpset -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c guru "
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
                raise HVControlException(self._logger, 'Timeout during command: ' + cmd)

        # cmd = "snmpset -v 2c -M /usr/share/snmp/mibs/  -m +WIENER-CRATE-MIB -c private 192.168.0.25  sysMainSwitch.0 i 1".format()

    def _get_cmd(self, name='sysMainSwitch.', ch='0'):
        cmd = "snmpget -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c public "
        cmd += self._mpod_ip + ' '
        cmd += name
        cmd += ch + ' '
        # self._logger.info('Subprocess: ' + cmd)

        # Start a subprocess
        start = time.time()
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        while proc.poll():
            time.sleep(0.1)
            if time.time() - start > 5:
                proc.terminate()
                raise HVControlException(self._logger, 'Timeout during command: ' + cmd)

        return proc.communicate()[0].decode("utf-8")



    def is_crate_on(self):
        '''
        Returns True if the crate is ON
        '''
        ret = self._get_cmd(name='sysMainSwitch.', ch=str(0))

        if 'on' in ret:
            return True

        return False


    def hv_on(self, prm_id=1):
        '''
        Sets the HV ON.
        '''
        channel = self._negative_channels[prm_id]
        print('self._negative_channels[prm_id]', self._negative_channels[prm_id])
        self._set_cmd(name='outputSwitch.u', ch=str(channel), t='i', value='1')

        channel = self._positive_channels[prm_id]
        print('self._positive_channels[prm_id]', self._positive_channels[prm_id])
        self._set_cmd(name='outputSwitch.u', ch=str(channel), t='i', value='1')

        return


    def hv_off(self, prm_id=1):
        '''
        Sets the OFF
        '''
        channel = self._negative_channels[prm_id]
        self._set_cmd(name='outputSwitch.u', ch=str(channel), t='i', value='0')

        channel = self._positive_channels[prm_id]
        self._set_cmd(name='outputSwitch.u', ch=str(channel), t='i', value='0')

        return


    def set_hv_value(self, posneg, value, prm_id=1):
        '''
        Sets HV value

        args:
        posneg: 'pos' or 'neg'
        '''

        if posneg == 'pos':
            channel = self._positive_channels[prm_id]
            self._set_cmd(name='outputVoltage.u', ch=str(channel), t='F', value=str(value))
        elif posneg == 'neg':
            channel = self._negative_channels[prm_id]
            self._set_cmd(name='outputVoltage.u', ch=str(channel), t='F', value=str(value))
        else:
            raise HVControlException(self._logger, 'posneg can only be pos or neg')
        return


    def get_hv_value(self, posneg, prm_id):
        '''
        Returns the HV values

        args:
        posneg: 'pos' or 'neg'
        prm_id: the prm id
        '''
        ret = None
        if posneg == 'pos':
            channel = self._positive_channels[prm_id]
            ret = self._get_cmd(name='outputVoltage.u', ch=str(channel))
        elif posneg == 'neg':
            channel = self._negative_channels[prm_id]
            ret = self._get_cmd(name='outputVoltage.u', ch=str(channel))
        else:
            raise HVControlException(self._logger, 'posneg can only be pos or neg')

        ret = ret.split('Float: ')[1][:-2]
        ref = float(ret)
        return ret

    def get_hv_status(self, posneg, prm_id):
        '''
        Returns wheter the HV is on or off

        args:
        posneg: 'pos' or 'neg'
        prm_id: the prm id
        '''
        ret = None
        if posneg == 'pos':
            channel = self._positive_channels[prm_id]
            ret = self._get_cmd(name='outputSwitch.u', ch=str(channel))
        elif posneg == 'neg':
            channel = self._negative_channels[prm_id]
            ret = self._get_cmd(name='outputSwitch.u', ch=str(channel))
        else:
            raise HVControlException(self._logger, 'posneg can only be pos or neg')

        ret = ret.split('INTEGER: ')[1][:-4]
        if ret == 'on':
            return True
        return False



