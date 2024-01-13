USB-Serial Persistent Name
===========================================

Get the Arduino information:

.. code-block:: bash

    -bash-4.2$ lsusb
    Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 001 Device 004: ID 0557:2419 ATEN International Co., Ltd
    Bus 001 Device 003: ID 0557:7000 ATEN International Co., Ltd Hub
    Bus 001 Device 007: ID 2341:8041 Arduino SA
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub


Here, the vendor ID is 2341, while the product ID is 8041.
We can now set up a udev rule. To do this, we need to create
a new file in /etc/udev/rules.d, for example "99-usb-serial.rules",
containing the following:

.. code-block:: bash

    SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="8041", SYMLINK+="arduino"

Then, unplug the device and plug it back in, and the arduino will be available
from "/dev/arduino":

.. code-block:: bash

    -bash-4.2$ ls -l /dev/arduino
    lrwxrwxrwx 1 root root 7 Apr 12 12:18 /dev/arduino -> ttyACM0


