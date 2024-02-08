'''
Contains data storage class for purity monitor data.
'''
import os
import logging
import paramiko
from scp import SCPClient


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

    def store_folder(self, foldername):
        '''
        Stores an entire folder

        Args:
            foldername (string): The full path of the folder to store

        Returns:
            bool: True is copy was successful
        '''
        self._logger.info(f"Storing folder {foldername} to {self._config['data_storage_host']}.")

        if not self._folder_exists(foldername):
            return False

        # Open an SSH tunnel
        with paramiko.SSHClient() as client:

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self._config['data_storage_host'],
                           username=self._config['data_storage_username'],
                           gss_auth=True)


            # Open an SCP client and copy the folder
            scp = SCPClient(client.get_transport())
            scp.put(foldername, recursive=True, remote_path=self._config['data_storage_path'])

        return True


    def _folder_exists(self, foldername):
        '''
        Checks if the folder exists

        Args:
            foldername (string): The full path of the folder to store
        '''
        return os.path.isdir(foldername)







