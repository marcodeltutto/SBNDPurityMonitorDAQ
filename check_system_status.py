#! /usr/bin/python3
# Checks that all PrM systems ara available




import os
from rich.console import Console
from rich.table import Table

table = Table(title="Check System Status")

table.add_column("Item", justify="right", style="cyan", no_wrap=True)
table.add_column("Status", style="magenta")
table.add_column("Notes", style="black")


#
# Import Settings
#
import yaml
settings = os.path.join(os.path.dirname(__file__), 'settings.yaml')

with open(settings) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
# print('Config:', yaml.dump(config), sep='\n')



#
# ATS Digitizers
#
import sbndprmdaq.digitizer.atsapi as ats

n_systems = ats.numOfSystems()
n_boards = ats.boardsFound()

print(f'Number of ATS systems: {n_systems}.')
print(f'Number of ATS boards: {n_boards}.')

if n_systems == 0:
    table.add_row("ATS Digitizers", "Not Found", f"# Systems {n_systems}")
else:
    table.add_row("ATS Digitizers", "Found", f"# Systems {n_systems}")

#
# Digilent Digitizer
#
import paramiko
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(config['adpro_ip'],
                username=config['adpro_username'],
                password=config['adpro_password'])
except:
    table.add_row("Digilent Digitizer", "Not Found", f"IP: {config['adpro_ip']}")
else:
    table.add_row("Digilent Digitizer", "Found", f"IP: {config['adpro_ip']}")


#
# MPODs
#

import time
import subprocess

for i, ip in enumerate([config['mpod_ip'], config['mpod_ip']]):
    cmd = f"snmpwalk -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c public {config['mpod_ip']} outputName"

    start = time.time()
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while proc.poll():
        time.sleep(0.1)
        if time.time() - start > 5:
            proc.terminate()
            print('Timeout during command: ', cmd)

    # print(proc.communicate()[0].decode("utf-8"))
    stdout, stderr = proc.communicate()
    message = stdout.decode("utf-8") + ' ' + stderr.decode("utf-8")
    if 'No Such Instance' in message:
        table.add_row(f"MPOD {i}", "Not Found", f"IP: {ip}")
    elif 'Timeout' in message:
        table.add_row(f"MPOD {i}", "Not Found", f"IP: {ip}")
    else:
        table.add_row(f"MPOD {i}", "Found", f"IP: {ip}")




#
# Arduino
#

import pyfirmata

try:
    board = pyfirmata.Arduino('/dev/arduino')
except:
    table.add_row("Arduino", "Not Found", "/dev/arduino")
else:
    table.add_row("Arduino", "Found", "/dev/arduino")

console = Console()
console.print(table)

os.remove('/tmp/ATSApi.log')
