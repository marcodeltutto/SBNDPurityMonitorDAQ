Take PrM Data
===================



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
___________________________

To take a run, simply click on Start. Note that the two internal purity monitors (PrM 1 and 2) are bounded together as we use the same flash lamp for both.

The DAQ can also run the purity monitors automatically every N minutes. This is currenlty set to 30 minutes at the moment and it's hardcoded in the DAQ. Issue: https://github.com/marcodeltutto/SBNDPurityMonitorDAQ/issues/29.



Setting the HV values
___________________________

Default HV values are specified in ``settings.yaml`` in the root folder of the DAQ. These are the values set when the DAQ is started.

To take a special run with different HV values, with the DAQ open, click on Menu, then HV Settings. You will be able to set the HV values for the Anode, Cathode, and Anode Grid. A toggle button allows switching the HV on and off. Remember to save the settings before exiting. The sensed HV values are displayed on the main DAQ window. Note that when you take a run, the DAQ automatically ramps the HV up and then down at the end of the run, so you don't have to manually turn the HV ON on the HV Settings page. This toggle is only available here in case we need to debug issues with the HV. 

HV settings should ensure that the "transparency requirement" is satisfied. This is true for the default values.



Output files
___________________________

Output files for each run are automatically saved on the local disk on the server: ``/home/nfs/sbndprm/purity_monitor_data``.

Additionally, they are automatically copied at the end of each run to sbndgpvm, on disk, on: ``/exp/sbnd/data/purity_monitors/``.

Files can be saved in both numpy archive ``.npz`` and simple ``.txt`` format. Which format to use can be specifed in the ``settings.yaml`` file in the root folder of the DAQ. We should probably keep both formats for now. Additionally, if the quick data analysis is being run, a plot in ``.png`` format is also saved which contains the waveforms and the estimated lifetime.

To look at these data, the easiest thing is to copy the files from sbndgvm to your local machine. A GitHub repository exists which contains scripts to plot and analyze the data:

https://github.com/marcodeltutto/PrMAnalysis (ask Marco to be added if you get a 404 and don't have access)



