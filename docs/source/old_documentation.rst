Old Documentation
=================


FNAL DAQ Systems
---------------------


Check here https://appora-cert.fnal.gov/pls/cert/sysadmin.search using your Fermilab ID if you are an administrator of the computer.

If not, go to http://appora.fnal.gov/pls/default/node_registration.html and register yourself as administrator.

Check here: http://appora.fnal.gov/misnet/systemName.html, with MAC address.

List all Fermilab clusters: https://appora-cert.fnal.gov/pls/cert/sysadmin.cluster_list
Add computer to cluster "SWS-SBND-TESTSTAND": https://appora-cert.fnal.gov/pls/cert/sysadmin.show_cluster?this_cluster_id=427422


Fermilab Kerberos on Ubuntu
---------------------------

Tested with 20.04.1 LTS.

General instructions:
https://fermi.servicenowservices.com/kb_view.do?sys_kb_id=443f19716fa4ed0032544d1fde3ee4fb.

From a freash Ubuntu installation.

Synch time using internet:

.. code-block:: bash

    sudo apt-get install ntp


Install Kerberos:

.. code-block:: bash

    sudo apt-get install krb5-user


Enter ``FNAL.GOV`` when prompted.

Get ``krb5.conf`` from https://authentication.fnal.gov/krb5conf/
and placed it in ``/etc/krb5.conf``.

Install openssh:

.. code-block:: bash

    sudo apt-get install openssh-client openssh-server


In ``/etc/ssh/sshd_config`` add:

.. code-block:: bash

    Protocol 2
    RSAAuthentication no
    PubkeyAuthentication no
    PasswordAuthentication no
    ChallengeResponseAuthentication no
    UsePAM yes
    KerberosAuthentication yes
    KerberosOrLocalPasswd no
    KerberosTicketCleanup yes
    GSSAPIAuthentication yes
    GSSAPIKeyExchange yes
    GSSAPICleanupCredentials yes
    X11Forwarding yes


In ``/etc/hosts`` add:

.. code-block:: bash

    131.225.179.214 puritymondaq1.fnal.gov puritymondaq1

or similar, and replace any line with `puritymondaq1` if already there.

Restart the ssh service:

.. code-block:: bash

    sudo systemctl restart sshd.service


Create a Kerberos keytab:

.. code-block:: bash

    kadmin -p host/puritymondaq1.fnal.gov -q "ktadd -k krb5.keytab host/puritymondaq1.fnal.gov"

and place it in ``/etc/krb5.keytab``.

Add a ``.k5login`` file to the home directory of any account to which you want to be able to log in remotely,
and include the appropriate principals which are allowed to log into the account. Ex, put:

.. code-block:: bash

    mdeltutt@FNAL.GOV



SL7 Setup
--------

Bla 

.. code-block:: bash
	sudo yum install qtcreator


.. code-block:: bash

	yum install gcc openssl-devel bzip2-devel libffi-devel -y
	curl -O https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz
	tar -xzf Python-3.8.1.tgz
	cd Python-3.8.1/
	./configure --enable-optimizations
	make


Ubuntu Setup
-----------

.. code-block:: bash

    sudo apt-get install python3-distutils
    sudo apt-get install python3-apt

    sudo apt-get install curl
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python3 get-pip.py


Get python packages:

.. code-block:: bash

    sudo apt-get install --reinstall libxcb-xinerama0


Get the parallel port to work:

.. code-block:: bash

    sudo chmod a+rw /dev/parport0
    sudo chmod 666 /dev/parport0
    sudo rmmod lp


