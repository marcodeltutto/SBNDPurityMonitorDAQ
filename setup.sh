#!/usr/bin/bash

# Test PyQt5
if ! python3 -c "import PyQt5" &> /dev/null; then
    echo "Warning: can not use evd due to missing package PyQt5"
    return
fi

# Test PyQtGraph
if ! python3 -c "import pyqtgraph" &> /dev/null; then
    echo "Warning: can not use evd due to missing package pyqtgraph"
    return
fi

# Test argparse
if ! python3 -c "import argparse" &> /dev/null; then
    echo "Warning: can not use evd due to missing package argparse"
    return
fi

# Test pyyaml
if ! python3 -c "import yaml" &> /dev/null; then
    echo "Warning: can not use evd due to missing package yaml"
    return
fi

# Test qdarkstyle
if ! python3 -c "import qdarkstyle" &> /dev/null; then
    echo "Warning: can not use evd due to missing package qdarkstyle"
    return
fi

# Test pyfirmata
if ! python3 -c "import pyfirmata" &> /dev/null; then
    echo "Warning: can not use evd due to missing package pyfirmata"
    return
fi

echo "All python packages installed and found."