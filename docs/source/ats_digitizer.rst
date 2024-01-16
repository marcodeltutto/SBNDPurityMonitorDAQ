ATS Digitizer Drivers Installation (SL7)
===========================================

SL7
---------------

### ATS310 Drivers


Download file
ftp://release@ftp.alazartech.com/outgoing/linux/CentOS/7/3.10.0-1062.9.1.el7.x86_64/ats310-7.1.1-2.x86_64.rpm

.. code-block:: bash

	user "release"
	password empty


Then, in the Downloads folder:

.. code-block:: bash

	sudo yum install ./ats310-7.1.1-2.x86_64.rpm



### libats Library

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/CentOS/7/libats-7.3.0-1.x86_64.rpm
Then, in the Downloads folder:

.. code-block:: bash

	sudo yum install ./libats-7.3.0-1.x86_64.rpm



### Front Panel Library

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/CentOS/7/alazar-front-panel-0.4.3-1.x86_64.rpm

Then, in the Downloads folder:

.. code-block:: bash

	sudo yum install ./alazar-front-panel-0.4.3-1.x86_64.rpm


Check is the oscilloscope works by running

.. code-block:: bash

	/usr/local/AlazarTech/bin/AlazarFrontPanel



### Alazar SDK

Download file
https://www.alazartech.com/Support/Download%20Files/ats-sdk-centos.zip

Then in the Downloads folder:

.. code-block:: bash

	sudo apt install unzip
	unzip ats-sdk-debian.zip
	sudo yum install ./ats-devel-7.4.0-1.noarch.rpm


Ubuntu
-------

### ATS310 Drivers

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/Ubuntu/20.04/drivers-ats310-dkms_7.3.0_amd64.deb

.. code-block:: bash

    user "release"
    password empty


Then, in the Downloads folder:

.. code-block:: bash

    sudo apt install ./drivers-ats310-dkms_7.3.0_amd64.deb



### libats Library

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/Ubuntu/libats/libats_7.3.0_amd64.deb

Then, in the Downloads folder:

.. code-block:: bash

    sudo apt install ./libats_7.3.0_amd64.deb



### Front Panel Library

Download file
ftp://release@ftp.alazartech.com/outgoing/linux/Ubuntu/alazar-front-panel/alazar-front-panel_0.4.3-1_amd64.deb

Then, in the Downloads folder:

.. code-block:: bash

    sudo apt install ./alazar-front-panel_0.4.3-1_amd64.deb


Check is the oscilloscope works by running

.. code-block:: bash

    /usr/local/AlazarTech/bin/AlazarFrontPanel



### Alazar SDK


Download file
https://www.alazartech.com/Support/Download%20Files/ats-sdk-debian.zip

Then in the Downloads folder:

.. code-block:: bash

    sudo apt install unzip
    unzip ats-sdk-debian.zip
    sudo apt install ./ats-devel_7.4.0_amd64.deb



