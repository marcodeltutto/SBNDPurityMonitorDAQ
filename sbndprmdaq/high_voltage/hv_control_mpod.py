'''
Contains class that controls the MPOD HV module
'''
import subprocess
import time
from .hv_control_base import HVControlBase, HVControlException


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
        super().__init__(prm_ids=prm_ids, config=config)

        #
        # Setting IP MPOD address
        #
        if 'prm_id_to_mpod_ip' not in config:
            raise HVControlException(self._logger, 'Missing prm_id_to_mpod_ip in config.')

        self._prm_id_to_mpod_ip = config['prm_id_to_mpod_ip']

        # Check if the HV crate is on or off
        for prm_id, mpod_ip in self._prm_id_to_mpod_ip.items():

            self._logger.info(f'Looking at {prm_id}: {mpod_ip}')

            if not self.is_crate_on(mpod_ip):
                self._logger.info(f'HV Crate is OFF for PrM {prm_id}? Try to turn it on...')
                # Turn crate on
                self._logger.info(f'Turning crate ON for PrM {prm_id}. Wait for 10 seconds...')
                self._set_cmd(ip=mpod_ip, name='sysMainSwitch.', ch=str(0), t='i', value='1')
                time.sleep(10)
                self._logger.info('...done.')

                # Check again
                if not self.is_crate_on(mpod_ip):
                    self._logger.error(f'Cannot turn HV Crate ON for PrM {prm_id}.')
                    raise HVControlException(self._logger, f'Cannot turn HV Crate ON for PrM {prm_id}.')


        #
        # Setting HV channels
        #
        self._anode_channels = {}
        self._anodegrid_channels = {}
        self._cathode_channels = {}
        for prm_id in prm_ids:
            if (f'mpod_prm{prm_id}_anode_ch' not in config) \
              or (f'mpod_prm{prm_id}_anodegrid_ch' not in config) \
              or (f'mpod_prm{prm_id}_cathode_ch' not in config):
                raise HVControlException(self._logger,
                                         f'Missing mpod_prm{prm_id}_anode_ch \
                                         or mpod_prm{prm_id}_anodegrid_ch \
                                         or mpod_prm{prm_id}_cathode_ch in config.')
            self._anode_channels[prm_id] = config[f'mpod_prm{prm_id}_anode_ch']
            self._anodegrid_channels[prm_id] = config[f'mpod_prm{prm_id}_anodegrid_ch']
            self._cathode_channels[prm_id] = config[f'mpod_prm{prm_id}_cathode_ch']

        self._logger.info('HVControlMPOD created.')

    #pylint: disable=invalid-name, too-many-arguments
    def _set_cmd(self, ip='', name='sysMainSwitch.', ch='0', t='i', value='0'):
        cmd = "snmpset -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c guru "
        cmd += ip + ' '
        cmd += name
        cmd += ch + ' '
        cmd += t + ' '
        cmd += value
        self._logger.info(f'Subprocess: {cmd}')

        # Start a subprocess
        start = time.time()
        with subprocess.Popen(cmd.split()) as proc:
            while proc.poll():
                time.sleep(0.1)
                if time.time() - start > 5:
                    proc.terminate()
                    raise HVControlException(self._logger, 'Timeout during command: ' + cmd)

        # cmd = "snmpset -v 2c -M /usr/share/snmp/mibs/  -m +WIENER-CRATE-MIB -c private 192.168.0.25  sysMainSwitch.0 i 1".format()

    def _get_cmd(self, ip='', name='sysMainSwitch.', ch='0', extra_flags=''):
        cmd = "snmpget -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c public "
        if extra_flags: # '-OUvq' for returning value only
            cmd += extra_flags + ' '
        cmd += ip + ' '
        cmd += name
        cmd += ch + ' '
        # self._logger.info('Subprocess: ' + cmd)

        # Start a subprocess
        start = time.time()

        with subprocess.Popen(cmd.split(), stdout=subprocess.PIPE) as proc:
            while proc.poll():
                time.sleep(0.1)
                if time.time() - start > 5:
                    proc.terminate()
                    raise HVControlException(self._logger, 'Timeout during command: ' + cmd)

            return proc.communicate()[0].decode("utf-8")

    def is_crate_on(self, ip):
        '''
        Returns True if the crate is ON
        '''
        try:
            ret = self._get_cmd(ip=ip, name='sysMainSwitch.', ch=str(0))
            print('ret', ret)
            if 'on' in ret:
                return True
        except ValueError as err:
            self._logger.error(err)
            self._logger.error(f'Cannot communicate with HV Crate at {ip}. Got ValueError.')
            return False
        return False


    def hv_on(self, prm_id=1):
        '''
        Sets the HV ON.
        '''
        ip = self._prm_id_to_mpod_ip[prm_id]

        channel = self._cathode_channels[prm_id]
        self._set_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), t='i', value='1')

        channel = self._anode_channels[prm_id]
        self._set_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), t='i', value='1')

        channel = self._anodegrid_channels[prm_id]
        self._set_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), t='i', value='1')


    def hv_off(self, prm_id=1):
        '''
        Sets the OFF
        '''
        ip = self._prm_id_to_mpod_ip[prm_id]

        channel = self._cathode_channels[prm_id]
        self._set_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), t='i', value='0')

        channel = self._anode_channels[prm_id]
        self._set_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), t='i', value='0')

        channel = self._anodegrid_channels[prm_id]
        self._set_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), t='i', value='0')


    def set_hv_value(self, item, value, prm_id=1):
        '''
        Sets HV value

        Args:
            item: 'anode', 'anodegrid', or 'cathode',
        '''
        ip = self._prm_id_to_mpod_ip[prm_id]

        if item == 'anode':
            channel = self._anode_channels[prm_id]
            self._set_cmd(ip=ip, name='outputVoltage.u', ch=str(channel), t='F', value=str(value))
        elif item == 'anodegrid':
            channel = self._anodegrid_channels[prm_id]
            self._set_cmd(ip=ip, name='outputVoltage.u', ch=str(channel), t='F', value=str(value))
        elif item == 'cathode':
            channel = self._cathode_channels[prm_id]
            self._set_cmd(ip=ip, name='outputVoltage.u', ch=str(channel), t='F', value=str(value))
        else:
            raise HVControlException(self._logger, 'item can only be anode, anodegrid, or cathode')


    def get_hv_value(self, item, prm_id=1):
        '''
        Returns the HV set voltage values

        Args:
            item: 'anode', 'anodegrid', or 'cathode'
            prm_id: the prm id
        '''
        ip = self._prm_id_to_mpod_ip[prm_id]

        ret = None
        if item == 'anode':
            channel = self._anode_channels[prm_id]
            ret = self._get_cmd(ip=ip, name='outputVoltage.u', ch=str(channel), extra_flags='-OUvq')
        elif item == 'anodegrid':
            channel = self._anodegrid_channels[prm_id]
            ret = self._get_cmd(ip=ip, name='outputVoltage.u', ch=str(channel), extra_flags='-OUvq')
        elif item == 'cathode':
            channel = self._cathode_channels[prm_id]
            ret = self._get_cmd(ip=ip, name='outputVoltage.u', ch=str(channel), extra_flags='-OUvq')
        else:
            raise HVControlException(self._logger, 'item can only be anode, anodegrid, or cathode')

        ret = float(ret)
        return ret

    def get_hv_sense_value(self, item, measure='voltage', prm_id=1):
        '''
        Returns the HV sensed values

        Args:
            item: 'anode', 'anodegrid', or 'cathode'
            measure: 'voltage', 'current', or 'temperature'
            prm_id: the prm id
        '''
        if measure == 'voltage':
            cmd_name = 'outputMeasurementTerminalVoltage.u'
            ret_type = float
        elif measure == 'current':
            cmd_name = 'outputMeasurementCurrent.u'
            ret_type = float
        elif measure == 'temperature':
            cmd_name = 'outputMeasurementTemperature.u'
            ret_type = int
        else:
            raise HVControlException(
                self._logger, 'measure can only be voltage, current, or temperature'
            )

        ip = self._prm_id_to_mpod_ip[prm_id]

        ret = None
        if item == 'anode':
            channel = self._anode_channels[prm_id]
            ret = self._get_cmd(ip=ip, name=cmd_name, ch=str(channel), extra_flags='-OUvq')
        elif item == 'anodegrid':
            channel = self._anodegrid_channels[prm_id]
            ret = self._get_cmd(ip=ip, name=cmd_name, ch=str(channel), extra_flags='-OUvq')
        elif item == 'cathode':
            channel = self._cathode_channels[prm_id]
            ret = self._get_cmd(ip=ip, name=cmd_name, ch=str(channel), extra_flags='-OUvq')
        else:
            raise HVControlException(self._logger, 'item can only be anode, anodegrid, or cathode')

        ret = ret_type(ret)

        return ret

    def get_hv_status(self, item, prm_id=1):
        '''
        Returns wheter the HV is on or off

        args:
        item: 'anode', 'anodegrid', or 'cathode',
        prm_id: the prm id
        '''
        ip = self._prm_id_to_mpod_ip[prm_id]

        ret = None
        if item == 'anode':
            channel = self._anode_channels[prm_id]
            ret = self._get_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), extra_flags='-OUvq')
        elif item == 'anodegrid':
            channel = self._anodegrid_channels[prm_id]
            ret = self._get_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), extra_flags='-OUvq')
        elif item == 'cathode':
            channel = self._cathode_channels[prm_id]
            ret = self._get_cmd(ip=ip, name='outputSwitch.u', ch=str(channel), extra_flags='-OUvq')
        else:
            raise HVControlException(self._logger, 'item can only be anode, anodegrid, or cathode')

        print('get_hv_status ret:', ret)
        if ret == 'on':
            return True
        return False
