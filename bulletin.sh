cd /local/repository

echo "Installing Required Packages..."

echo "Installing pip"
sudo apt update
sudo apt --assume-yes install python3-pip

echo "Installing gmp"
sudo apt-get --assume-yes install libgmp-dev

echo "Installing Python packages"
pip3 install Pyro4
pip3 install numpy

echo "Building"
make

echo "Starting Nameserver"
pyro4-ns -p $1 &

# Wait for nodes to start
# sleep 20

#cd network
#python3 bulletin.py
