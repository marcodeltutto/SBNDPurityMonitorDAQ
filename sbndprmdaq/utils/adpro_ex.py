import requests
import paramiko
from sshtunnel import SSHTunnelForwarder


server = SSHTunnelForwarder("192.168.2.10", ssh_username="digilent", ssh_password="digilent", remote_bind_address=('127.0.0.1', 8000))
server.start()
url = 'http://127.0.0.1:' + str(server.local_bind_port)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.2.10", username="digilent", password="digilent")
command = 'cd adpro_api '
command += '/home/digilent/.local/bin/uvicorn main:app --reload'
ssh.exec_command(command)



response = requests.get(url + f"/lamp_frequency/10")