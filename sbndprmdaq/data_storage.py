'''
Contains data storage class for purity monitor data.
'''
import os
import logging
import subprocess
import time
import copy
import paramiko
from scp import SCPClient
import pandas as pd

#pylint: disable=too-few-public-methods,duplicate-code
class DataStorage():
    '''
    A class that handles storage of purity monitor data
    '''

    def __init__(self, config):
        '''
        Constructor.

        Args:
            config (dict): The overall configuration.
        '''
        self._logger = logging.getLogger(__name__)
        self._config = config


    def kinit(self):
        '''
        Authenticates via a keytab
        '''

        os.environ["KRB5CCNAME"] = "/tmp/krb5cc_sbndprm"

        cmd = 'kinit -kt /var/kerberos/krb5/user/25081/client.keytab sbndprm/sbnd-prm01.fnal.gov@FNAL.GOV'

        start = time.time()

        with subprocess.Popen(cmd.split()) as proc:
            while proc.poll():
                time.sleep(0.1)
                if time.time() - start > 5:
                    proc.terminate()
                    self._logger.error(f'Timeout during command: {cmd}')

        self._logger.info("Kerberos certificate obtained.")

    def check_ticket(self):
        '''
        Checks if a valid kerberos ticket is available
        '''

        self._logger.info('Checking ticket...')

        cmd = 'klist -f'

        start = time.time()

        with subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            while proc.poll():
                time.sleep(0.1)
            if time.time() - start > 5:
                proc.terminate()
                self._logger.error(f'Timeout during command: {cmd}')

            comm = proc.communicate()
            out = comm[0].decode("utf-8")
            err = comm[1].decode("utf-8")

            self._logger.info(f'out: {out}')
            self._logger.info(f'err: {err}')

            if 'No credentials cache found' in err:
                self._logger.info('no ticket found...')
                return False

        return True

    def store_files(self, filenames):
        '''
        Stores an entire folder

        Args:
            filenames (list): The list of strings containind the full path of the files to store

        Returns:
            bool: True is copy was successful
        '''

        #pylint: disable=broad-exception-caught
        try:
            # if not self.check_ticket():
                # self._logger.info('Ticket expired. Regenerating.')
            self.kinit()

            real_filenames = []
            self._logger.info(f"Storing these files to {self._config['data_storage_host']}:{self._config['data_storage_path']}:")
            for filename in filenames:
                if self._file_exists(filename):
                    self._logger.info(filename)
                    real_filenames.append(filename)
                else:
                    self._logger.info(f"File {filename} does not exist.")


            # Open an SSH tunnel
            with paramiko.SSHClient() as client:

                self._logger.info("Opened SSH client.")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(self._config['data_storage_host'],
                               username=self._config['data_storage_username'],
                               gss_auth=True)


                # Open an SCP client and copy the folder
                with SCPClient(client.get_transport()) as scp:
                    self._logger.info("Opened SCP.")
                    for fname in real_filenames:
                        scp.put(fname, recursive=True, remote_path=self._config['data_storage_path'])

            return True

        except Exception as err:
            self._logger.error(f"Unexpected {err}, {type(err)}")
            return False


    def _folder_exists(self, foldername):
        '''
        Checks if the folder exists

        Args:
            foldername (string): The full path of the folder to store
        '''
        return os.path.isdir(foldername)


    def _file_exists(self, filename):
        '''
        Checks if the file exists

        Args:
            filename (string): The full path of the file to store
        '''
        return os.path.isfile(filename)


    def update_dataframe(self, measurement, prm_id):
        '''
        Updates the dataframe containing all the purity measurements

        Args:
            measurement (dict): the latest measturement
            prm_id (int): the purity monitor ID
        '''
        #pylint: disable=invalid-name

        self._logger.warning('Updating dataframe.')

        if measurement is None:
            self._logger.warning('No measurement available to save to dataframe.')
            return

        dataframe_file_name = self.get_dataframe_path()

        if dataframe_file_name is None:
            self._logger.warning('No dataframe path. No measurement will be saved to the dataframe.')
            return

        if not os.path.exists(dataframe_file_name):
            self._logger.info('Measurements dataframe file doesnt exist. One will be created.')
        else:
            self._logger.info('Measurements dataframe file exists. It will be updated.')

        df = pd.read_csv(dataframe_file_name)

        meas = copy.copy(measurement)
        meas['prm_id'] = prm_id
        meas['drifttime'] = meas.pop('td')
        meas['lifetime'] = meas.pop('tau')
        meas['hv_c'] = meas.pop('v_c')
        meas['hv_ag'] = meas.pop('v_ag')
        meas['hv_a'] = meas.pop('v_a')

        df = df.append(meas, ignore_index=True)

        df.to_csv(dataframe_file_name)

    def get_dataframe_path(self):
        '''
        Returns the path to the dataframe
        '''

        if self._config['data_files_path'] is None:
            self._logger.warning('data_files_path is not set.')
            return None

        if not os.path.exists(self._config['data_files_path']):
            self._logger.error(f'data_files_path {self._config["data_files_path"]} is not a real path.')
            raise RuntimeError()

        dataframe_file_name = self._config['data_files_path'] + '/prm_measurements.csv'

        return dataframe_file_name
