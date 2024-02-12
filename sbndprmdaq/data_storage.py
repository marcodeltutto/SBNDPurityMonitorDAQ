'''
Contains data storage class for purity monitor data.
'''
import os
import logging
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

    def store_files(self, filenames):
        '''
        Stores an entire folder

        Args:
            filenames (list): The list of strings containind the full path of the files to store

        Returns:
            bool: True is copy was successful
        '''
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
