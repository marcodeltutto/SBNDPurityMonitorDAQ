import os, yaml
import paramiko

# Read YAML settings
settings = os.path.join(os.path.dirname(__file__), '../settings.yaml')
with open(settings) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

try:
    # Open an SSH tunnel with the digitizer
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config['adpro_ip'],
                   username=config['adpro_username'],
                   password=config['adpro_password'])

    # Remove the current API, if any
    stdin, stdout, stderr = client.exec_command("echo hello")
    print('stdout', stdout.readlines())
    print('stderr', stderr.readlines())

except Exception as inst:
    print("Something went wrong")
    print(inst)


