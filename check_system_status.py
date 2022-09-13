# This script has the effect of making DTR and RTS pins not
# being affected from the port being opened or closed,
# so they can be used as GPIO pins.





from rich.console import Console
from rich.table import Table

table = Table(title="Check System Status")

table.add_column("Item", justify="right", style="cyan", no_wrap=True)
table.add_column("Status", style="magenta")
# table.add_column("Box Office", justify="right", style="green")










# import sys
# sys.path.insert(1, '/home/nfs/mdeltutt/Documents/SBNDPurityMonitorDAQ')
# sys.path.insert(1, '../../')
#
# Digitizer
#

import sbndprmdaq.digitizer.atsapi as ats

n_systems = ats.numOfSystems()
n_boards = ats.boardsFound()

print(f'Number of ATS systems: {n_systems}.')
print(f'Number of ATS boards: {n_boards}.')

if n_systems == 0:
    table.add_row("Digitizers", "Not Found")
else:
    table.add_row("Digitizers", "Found")




#
# MPOD
#

import time
import subprocess

cmd = "snmpwalk -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c public 192.168.0.25 outputName"

start = time.time()
proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
while proc.poll():
    time.sleep(0.1)
    if time.time() - start > 5:
        proc.terminate()
        print('Timeout during command: ', cmd)

# print(proc.communicate()[0].decode("utf-8"))
if 'No Such Instance'  in proc.communicate()[0].decode("utf-8"):
    table.add_row("MPOD", "Not Found")
else:
    table.add_row("MPOD", "Found")




#
# Arduino
#

import pyfirmata

try:
    board = pyfirmata.Arduino('/dev/arduino')
except:
    table.add_row("Arduino", "Not Found")
else:
    table.add_row("Arduino", "Found")

console = Console()
console.print(table)


