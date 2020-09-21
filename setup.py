import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sbnd_purity_monitor_daq", # Replace with your own username
    version="0.0.1",
    author="Marco Del Tutto",
    author_email="mdeltutt@fnal.gov",
    description="The DAQ for the SBND purity monitors.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcodeltutto/SBNDPurityMonitorDAQ",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)