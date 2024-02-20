'''
Contains data storage class for purity monitor data.
'''
import os
import logging
import subprocess
import time
import paramiko
from scp import SCPClient

#pylint: disable=too-few-public-methods
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

        self.kinit()

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
                    self._logger.error('Timeout during command: ' + cmd)
        
        self._logger.info(f"Kerberos certificate obtained.")

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
                    self._logger.error('Timeout during command: ' + cmd)

            # out = proc.communicate()[0].decode("utf-8")
            err = proc.communicate()[1].decode("utf-8")

            self._logger.info('err: ' + err)

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

        if not self.check_ticket():
            self._logger.info('Ticket expired. Regenerating.')
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
