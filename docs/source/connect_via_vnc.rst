Connect via VNC
===========================================



Unix
---------------

To be written.


Windows
---------------

On the PrM machine:

.. code-block:: bash

	vncserver :1 -name username -depth 16 -geometry 1920x1080 -localhost

If you encounter this error:

.. code-block:: bash

	A VNC server is already running as :1

try a different port (replace ":1", with another number).

It will ask you to set a password.

On your Windows machine, create an ssh tunnel via:


.. code-block:: bash

	ssh -L 5902:localhost:5902 username@sbnd-prm-daq01.fnal.gov

Then, install TightVNC from https://www.tightvnc.com/download.html

Open TightVNC and write

.. code-block:: bash

	localhost:5901

Replace the last 1 with your port number.

Insert the password you previously set, and you should be able to connect.

