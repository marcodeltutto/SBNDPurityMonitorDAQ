Information for PrM Experts
===================

This page contains instructions for purity monitor experts.



Logging in and setting up
---------------
The DAQ is accessed from a VNC and it displays on the web browser. This is
similar to other SBND setups.

For this, you need to make sure you have been added to the `sbndprm` account (ask Marco).
This is the account for purity monitor experts.


VNC (Default)
____________

From terminal on your local machine create a tunnel (you must be connected to the `fgz` network, or use a VPN):

.. code-block:: bash

	ssh -L 8443:sbnd-prm01.fnal.gov:443 sbnd@sbnd-gateway01.fnal.gov

Then, go to the following link on your browser:

`https://localhost:8443 <https://localhost:8443>`_

Click connect and enter password (ask Marco).

The DAQ should already be running.



SSH
_____________________

The DAQ should only be run from the VNC session!
But the ssh access can be useful for other purposes.

To connect to the purity monitor server via ssh, from terminal on your local machine:

.. code-block:: bash

	ssh username@sbnd-gateway01.fnal.gov
	ssh sbndprm@sbnd-prm01.fnal.gov



Changing Display Resolution
___________________________

To change the resolution of the VNC display, from the VNC session on your browser, type ``xrandr`` which will show
all the available resolution, select the 1920x1200 by specifing the line number with option ``-s``. For example,
if 1920x1200 appears on the second line, do:

.. code-block:: bash

	xrandr -s 2

Running ``xrandr`` again should show your selection by adding a ``*`` next to 1920x1200.

If this doesn't change anything, click on the little noVNC arrorw on the left border of the browser.
Then `Settings > Scaling Mode > Local Scaling`. Finally, refresh your bowser page.



How to open the DAQ
---------------

Open a terminal, then:

Open a tunnel with the digitizer of the internal monitors:

.. code-block:: bash

	ssh -L 8000:localhost:8000 digilent@10.226.35.155
	cd AnalogDiscoveryPro
	sudo /home/digilent/.local/bin/uvicorn main:app --reload      # Start the API


Open another terminal tab and:

.. code-block:: bash

	cd
	cd SBNDPurityMonitorDAQ
	./check_system_status.py # checks that all systems are online
	./prm_gui.py             # runs the DAQ GUI


Take a run
------------

To take a run, simply click on Start. Note that the two internal purity monitors (PrM 1 and 2) are bounded together as we use the same flash lamp for both.

The DAQ can also run the purity monitors automatically every N minutes. This is currenlty set to 30 minutes at the moment and it's hardcoded in the DAQ. Issue: https://github.com/marcodeltutto/SBNDPurityMonitorDAQ/issues/29.



Setting the HV values
----------------------

Default HV values are specified in ``settings.yaml`` in the root folder of the DAQ. These are the values set when the DAQ is started.

To take a special run with different HV values, with the DAQ open, click on Menu, then HV Settings. You will be able to set the HV values for the Anode, Cathode, and Anode Grid. A toggle button allows switching the HV on and off. Remember to save the settings before exiting. The sensed HV values are displayed on the main DAQ window. Note that when you take a run, the DAQ automatically ramps the HV up and then down at the end of the run, so you don't have to manually turn the HV ON on the HV Settings page. This toggle is only available here in case we need to debug issues with the HV. 

HV settings should ensure that the "transparency requirement" is satisfied. This is true for the default values.



Output files
----------------------

Output files for each run are automatically saved on the local disk on the server: ``/home/nfs/sbndprm/purity_monitor_data``.

Additionally, they are automatically copied at the end of each run to sbndgpvm, on disk, on: ``/exp/sbnd/data/purity_monitors/``.

Files can be saved in both numpy archive ``.npz`` and simple ``.txt`` format. Which format to use can be specifed in the ``settings.yaml`` file in the root folder of the DAQ. We should probably keep both formats for now. Additionally, if the quick data analysis is being run, a plot in ``.png`` format is also saved which contains the waveforms and the estimated lifetime.

To look at these data, the easiest thing is to copy the files from sbndgvm to your local machine. A GitHub repository exists which contains scripts to plot and analyze the data:

https://github.com/marcodeltutto/PrMAnalysis (ask Marco to be added if you get a 404 and don't have access)






Troubleshooting
----------------

Many errors of type:

.. code-block:: bash

	requests.exceptions.ConnectionError:

The tunnel to the AnalogDiscoveryPro digitizer is down. Re-establish the tunnel as described at the beginning of this wiki.


The flash lamp energy cannot be set to 5000 mJ.










Overview
------------

SBND has a total of 3 purity monitors, two internal to the cryostat (called the "internals") and one in its own vessel located after the filters (called the "inline"). The internal monitors are on detector ground and the inline is on building ground, which necessitate keeping the electronics separate for the two types of monitors. Rack PM1 is located on the top of the cryostat and contains the electronics for the internal monitors, while rack PM2 is located on the cryo top platform and contains the electronics for the inline monitor. Each rack contains the purity monitor electronics module (which distributes the HV to the PrMs and picks up the signals), the power supply (ISEGs in MPODMini crates), and the Xe flash lamp. There is only one flash lamp on PM1, and this serves both purity monitors. PM2 rack, being on building ground, also hosts the purity monitor server (sbnd-prm01.fnal.gov). This server, via an optical uplink, is able to communicate with the power supply in PM2, but also with the one in PM1, and with the digitizers in PM1. This setup allows having a single server to control all 3 purity monitors.

Digitization
_____________

The digitization of the signals is done dfferently for the two types of monitors:
- the digitizer for the inline is located inside the server and is the same that MicroBooNE used. There are in fact 3 digitizers in that server, but we will only use one. This digitizers is called ATS310.
- the digitizer for the internal monitors (called AnalogDiscoveryPro, or ADPro) is instead new and is located on PM1 to avoid ground loops. It has a Linux kernel and this allows us ssh'ing to the digitizer itself, which can be done from the PrM server. Parts of the ADPro sofware are only compatible with AlmaLinux9, and not with ScientificLinux7 (currenlty used). Since an upgrade to SL7 is impossible, as it will break the inline ATS310 digitizer, a custom code has been written to have the ADPro, located here: https://github.com/marcodeltutto/AnalogDiscoveryPro/tree/main. This is a softare that runs on the digitizer itself, and it communicates with the outside world via an API.

Flash Lamp
____________

Flash lamp manuals are on https://sbn-docdb.fnal.gov/cgi-bin/sso/ShowDocument?docid=24074.

The two flash lamps are wired differently for the two monitors:

##Inline

This uses the MicroBooNE wiring and the lamp is set to "run" all the time but an interlock prevents it from flashing. The lamp interlock has 2 pins, when they are closed, the lamp flashed, otherwise it stops. In order to have some automation, a custom electronics module has been developed and installed in PM2. This module contains an Arduino connected to the server. The Arduino is further connected to a relay. The Arduino contains the PyFirmata firmaware, which allows us to contol the Arduino live from the server (https://github.com/marcodeltutto/SBNDPurityMonitorDAQ/blob/master/sbndprmdaq/digitizer/lamp_control_arduino.py). When ready to take a run, the DAQ tells the Arduino to close the relay, which is connected to the flash lamp, which then starts flashing. Note that there is no timeout here. If the lamp doesn't stop flashing, restarting the DAQ will re-establigh the connection to the Arduino and stop the lamp. 

### Manual turn one
The custom module has a switch that, if set to "Manual" allows closing the relay manually by pushing the "Lamp ON" button. This can be used to debug the connections withouth using the server and bypassing the Arduino. Make sure to switch it back to "Auto" when done! :) 

### Lamp Settings
The flash lamp needs to be set to "INT TRIG" on the front panel in order to be controlled via the "Lamp Control" signal.
The lamp energy should be set to 5000 mJ and the frequency to 10 Hz. We use 10 Hz because the flash intensity dimishes at 12 Hz, and going slower that 10 Hz means more time for a data acquisition in case we want to acquire multiple flashes. The first time you run the lamp you may see the energy decreasing, but it will go up to 5000 after a few flashes. 

##Internal

The wiring for the internal lamp has been changed from the MicroBooNE's one. Here the lamp is interlock is used as a real interlock and it's connected to the experiment interlock system. This prevents the lamp from flashing if PDS HV is on. The "Lamp Control" input is used to turn the lamp on and off. This input needs a TTL waveform and will flash everytime the TTL is up. This also allows us setting the flashing frequency, which is given by the TTL waveform frequency. In order to generate a TTL waveform, the ADPro digitizer is used, as it also provied two channels that are waveform generators. Channel 1 is used to generate a square waveform of 2 V amplitude and 0 V baseline, creating TTL signals. The ADPro digitizer is then used both for the digitization of the waveforms of the internal monitors, and for controlling the flash lamp.

### Manual turn one
To manually turn on the lamp, one needs to provide a TTL signal, either use an external waveform generator or use the ADPro, without the DAQ running. On the VNC session, with the tunnel to the ADPro in place, open Firefox (should be already open) and go to: 

- http://localhost:8000/lamp_control/off (turn the lamp off)
- http://localhost:8000/lamp_control/on (turn the lamp on)
- http://localhost:8000/lamp_frequency/10 (sets frequency to 10 Hz)

### Lamp Settings
The flash lamp needs to be set to "EXT TRIG" on the front panel in order to be controlled via the "Lamp Control" signal. The lamp energy should be set to 5000 mJ. The first time you run the lamp you may see the energy decreasing, but it will go up to 5000 after a few flashes.


## Lamp Reset

Sometimes the lamp enters in a funny state and you won't be able to change the energy level. In this case, a system reset is necessary. Instructions are on docdb https://sbn-docdb.fnal.gov/cgi-bin/sso/ShowDocument?docid=24074.


Power Supply
_____________

The system used two MPOD Mini crates in PM1 and PM2. The two crates host one positive (6 kV max) ISEG modules with 8 channels, and one negative (500 V max) ISEG module with 8 channels. The internal monitors use 4 channels of the positive one (two for the anodes and two for the anode grids) and two channels of the negative one (for the two cathodes). The inline monitor instead only used 2 of the positive channels, and one of the negative.

The power supplies are controlled by the DAQ running on the PrM server. This is done using the SNMP protocol. 
For debugging purposes, one may want to control the MPOD withouth the DAQ. For this one can consult the manual on https://sbn-docdb.fnal.gov/cgi-bin/sso/ShowDocument?docid=24074

For example, the following command will show all the set voltages on PM1:

.. code-block:: bash

	snmpwalk -v 2c -M /usr/share/snmp/mibs/ -m +WIENER-CRATE-MIB -c public 10.226.35.154 outputVoltage

The part of the DAQ that handles it is here: https://github.com/marcodeltutto/SBNDPurityMonitorDAQ/blob/master/sbndprmdaq/high_voltage/hv_control_mpod.py 

Note that the MPOD on PM2 has a display and controls which allows setting voltages, while PM1 does not. SNMP is the only way, and their Muse software only runs on Windows.

Note that this is not controlled via Phoebus/EPICS as other SBND's MPODs as it needs to be integrated with the purity monitor DAQ.


IP Addresses
______________

- MPOD PM1: 10.226.35.154
- MPOD PM2: 10.226.35.156
- ADPro PM1: 10.226.35.155


Using the Oscilloscope
_______________________

For debugging purposes, one can look at the signals with the scope, without using the DAQ.
Needed equipment:
- Oscilloscope: located in the cabinet on the mezzanine
- Cables: 2 RG-58 cables terminated with a BNC on one side, and with a LEMO on the other side. Two of these cables are avalable next to the PM2 rack 
