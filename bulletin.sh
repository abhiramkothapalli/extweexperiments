cd /local/repository

echo "Installing Required Packages..."

echo "Installing pip"
sudo apt update
sudo apt --assume-yes install python3-pip

echo "Installing gmp"
sudo apt-get --assume-yes install libgmp-dev

echo "Installing Python packages"
sudo python3 -m pip install Pyro4 numpy

echo "Building"
sudo make

echo "Starting Nameserver"
pyro4-ns -n $1 -p $2

# Wait for nodes to start
# sleep 20

#cd network
#python3 bulletin.py
