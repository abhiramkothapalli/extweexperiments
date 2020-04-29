cd /local/repository

echo "Installing Required Packages..."

echo "Installing pip"
sudo apt update
sudo apt --assume-yes install python3-pip

echo "Installing gmp"
sudo apt-get --assume-yes install libgmp-dev
sudo apt-get --assume-yes install swig

echo "Installing Python packages"
sudo python3 -m pip install Pyro4 numpy

echo "Building"
sudo make

echo "Starting Nameserver"
cd network
python3 nameserver.py

