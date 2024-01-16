# SBNDPurityMonitorDAQ

[![tests](https://github.com/marcodeltutto/SBNDPurityMonitorDAQ/actions/workflows/test.yml/badge.svg)](https://github.com/marcodeltutto/SBNDPurityMonitorDAQ/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/sbndpuritymonitordaq/badge/?version=latest)](https://sbndpuritymonitordaq.readthedocs.io/en/latest/?badge=latest)
![pylint](https://github.com/marcodeltutto/SBNDPurityMonitorDAQ/actions/workflows/pylint.yml/badge.svg)

This project is documented [here](https://sbndpuritymonitordaq.readthedocs.io/en/latest/).

## Run
```
./prm_gui.py
```

If running without a parallel/serial port, and without digitizer, for testing purposes:
```
./prm_gui.py --mock
```

## Run tests
```
pytest tests
```
