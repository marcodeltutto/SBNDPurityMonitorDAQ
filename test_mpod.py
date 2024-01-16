

import os
from rich.console import Console
from rich.table import Table

table = Table(title="Check System Status")

table.add_column("Item", justify="right", style="cyan", no_wrap=True)
table.add_column("Status", style="magenta")

import time
import subprocess

cmd = "snmpwalk -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c public 10.226.35.154 outputName"

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


