# Extractible Witness Encryption Experiments

## Dependencies

```
sudo apt-get --assume-yes install libgmp-dev
sudo apt-get --assume-yes install swig

sudo -H pip3 install --upgrade pip

sudo -H pip3 install grpcio-tools
sudo python3 -m pip install numpy

```


## Running

```
cd extweexperiments/
make
cd test
python3 benchmarking.py
```

