# Extractible Witness Encryption Experiments

This repository contains an implementation of the dynamic proactive secret sharing scheme presented by Goyal, Kothapalli, Masserova, Parno, and Song in the work "Storing and Retrieving Secrets on a Blockchain". This work can be found at https://eprint.iacr.org/2020/504

## Dependencies

```
sudo apt-get --assume-yes install libgmp-dev
sudo apt-get --assume-yes install swig

sudo -H pip3 install --upgrade pip

sudo -H pip3 install grpcio-tools
sudo python3 -m pip install numpy

```


## Building and Running

```
cd extweexperiments/
make
cd test
python3 benchmarking.py
```

