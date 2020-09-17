Ubuntu Setup

```
sudo apt-get install python3-distutils
sudo apt-get install python3-apt

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py
```

Get python packages:
```
sudo apt-get install --reinstall libxcb-xinerama0
```

Get the parallel port to work:
```
sudo chmod a+rw /dev/parport0
sudo chmod 666 /dev/parport0
sudo rmmod lp
```
