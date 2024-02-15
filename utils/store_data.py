'''
Script to store data
'''

import os
import logging
import paramiko
from scp import SCPClient
import yaml

# Read YAML settings
settings = os.path.join(os.path.dirname(__file__), '../settings.yaml')
with open(settings) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

print('Storing to:       ', config['data_storage_host'])
print('   at path:       ', config['data_storage_path'])
print('   with userename:', config['data_storage_username'])

# Files to store
real_filenames = [
    '/home/nfs/sbndprm/purity_monitor_data/sbnd_prm2_run_142_data_20240214-102925.npz',
]

with paramiko.SSHClient() as client:

    print("Opened SSH client.")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config['data_storage_host'],
                   username=config['data_storage_username'],
                   gss_auth=True)


    # Open an SCP client and copy the folder
    with SCPClient(client.get_transport()) as scp:
        print("Opened SCP.")
        for fname in real_filenames:
            print('Copying', fname)
            scp.put(fname, recursive=True, remote_path=config['data_storage_path'])
