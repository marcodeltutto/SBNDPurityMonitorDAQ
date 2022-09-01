Setup Instructions
===========================================

This page contains setup instructions to run the DAQ on SBND's `sbnd-prm-daq01` server.


Prerequisites
---------------

You need an account on the appropriate cluster. Fill out a `Test Stand Service Request Form <https://fermi.servicenowservices.com/wp/?id=evg_sc_cat_item&sys_id=b0a7f0b46f8ec200c6df5d412e3ee4b6&spa=1>`_ on Fermilab ServiceNow and ask that you be added to the SBND's SBND-PRM-DAQ01 machine. For Short description use "Request access to SBND's purity monitor server". Under "Please describe the request" specify that you would like to be added to the SBN DAQ clusters at DAB, PAB, and ND.


Logging in and setting up
---------------

Login to the purity monitor machine under your user name:

```bash=
ssh username@sbnd-prm-daq01.fnal.gov
```



```bash=
mkdir work_area
cd work_area
git clone https://github.com/marcodeltutto/SBNDPurityMonitorDAQ.git
cd SBNDPurityMonitorDAQ
python test.py
```




