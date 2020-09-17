Ubuntu Setup

```
sudo apt-get install python3-distutils
sudo apt-get install python3-apt

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py
```

Get the parallel port to work:
```
sudo chmod 666 /dev/parport0
sudo rmmod lp
```
