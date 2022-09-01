Setup Instructions
===========================================

This page contains setup instructions to run the DAQ on SBND's ``sbnd-prm-daq01`` server.


Prerequisites
---------------

You need an account on the appropriate cluster. Fill out a `Test Stand Service Request Form <https://fermi.servicenowservices.com/wp/?id=evg_sc_cat_item&sys_id=b0a7f0b46f8ec200c6df5d412e3ee4b6&spa=1>`_ on Fermilab ServiceNow and ask that you be added to the SBND's SBND-PRM-DAQ01 machine. For Short description use "Request access to SBND's purity monitor server". Under "Please describe the request" specify that you would like to be added to the SBN DAQ clusters at DAB, PAB, and ND.


Logging in and setting up
---------------

Login to the purity monitor machine under your user name:

.. code-block:: bash

	ssh username@sbnd-prm-daq01.fnal.gov

.. code-block:: bash

	mkdir work_area
	cd work_area
	git clone https://github.com/marcodeltutto/SBNDPurityMonitorDAQ.git
	cd SBNDPurityMonitorDAQ

	# Run the source script which checks if all needed packages are installed
	source setup.sh

Open the ``settings.yaml`` file and modify the ``data_files_path`` field to point to your area, for example
``/home/nfs/username/work_area/data/``. Make sure this directory exists.


Run the DAQ
---------------

Firts, check that all the components are visible:

.. code-block:: bash

	python3 check_system_status.py

You should see that all three components (digitizers, MPOD, and arduino) are all found.

To run the DAQ, simply run:

.. code-block:: bash

	./prm_gui.py


Setting the HV values
---------------

With the DAQ open, click on Menu, then HV Settings. You will be able to set the HV values for the Anode,
Cathode, and Anode Grid. A toggle button allows switching the HV on and off. Remember to save the settings
before exiting. The sensed HV values are displayed on the main DAQ window.















