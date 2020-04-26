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

echo "Waiting for ns to start"
sleep 600

echo "Starting Node"
cd /local/repository/network
python3 node.py $1 $2 $3 $4 $5
