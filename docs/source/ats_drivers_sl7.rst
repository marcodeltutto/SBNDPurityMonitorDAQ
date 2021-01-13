ATS Digitizer Drivers Installation (SL7)
===========================================


ATS310 Drivers
---------------

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/CentOS/7/3.10.0-1062.9.1.el7.x86_64/ats310-7.1.1-2.x86_64.rpm

.. code-block:: bash

	user "release"
	password empty


Then, in the Downloads folder:

.. code-block:: bash

	sudo yum install ./ats310-7.1.1-2.x86_64.rpm



libats Library
---------------

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/CentOS/7/libats-7.3.0-1.x86_64.rpm
Then, in the Downloads folder:

.. code-block:: bash

	sudo yum install ./libats-7.3.0-1.x86_64.rpm



Front Panel Library
--------------------

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/CentOS/7/alazar-front-panel-0.4.3-1.x86_64.rpm

Then, in the Downloads folder:

.. code-block:: bash

	sudo yum install ./alazar-front-panel-0.4.3-1.x86_64.rpm


Check is the oscilloscope works by running

.. code-block:: bash

	/usr/local/AlazarTech/bin/AlazarFrontPanel



Alazar SDK
---------------

Download file
https://www.alazartech.com/Support/Download%20Files/ats-sdk-centos.zip

Then in the Downloads folder:

.. code-block:: bash

	sudo apt install unzip
	unzip ats-sdk-debian.zip
	sudo yum install ./ats-devel-7.4.0-1.noarch.rpm



