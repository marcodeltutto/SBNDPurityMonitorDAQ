import os, yaml
import paramiko
from scp import SCPClient

# Read YAML settings
settings = os.path.join(os.path.dirname(__file__), '../settings.yaml')
with open(settings) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Download the repo containing the API
os.system("git clone https://github.com/marcodeltutto/AnalogDiscoveryPro.git")

try:
    # Open an SSH tunnel with the digitizer
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config['adpro_ip'],
                   username=config['adpro_username'],
                   password=config['adpro_password'])

    # Remove the current API, if any
    client.exec_command("rm -rf AnalogDiscoveryPro")

    # Open an SCP client with the digitizer and copy the repo there
    scp = SCPClient(client.get_transport())
    scp.put('AnalogDiscoveryPro', recursive=True, remote_path='~/')

except Exception as inst:
    print("Something went wrong")
    print(inst)

# Remove the repo from this machine
os.system("rm -rf AnalogDiscoveryPro")

