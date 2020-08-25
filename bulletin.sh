cd /local/repository

echo "Installing Required Packages..."

echo "Installing pip"
sudo apt update
sudo apt --assume-yes install python3-pip

echo "Installing gmp"
sudo apt-get --assume-yes install libgmp-dev
sudo apt-get --assume-yes install swig

echo "Installing Python packages"
sudo python3 -m pip install numpy

echo "Building"
sudo make

echo "GRPC"
cd /local/repository/network
sudo -H pip3 install --upgrade pip
sudo python3 -m pip install grpcio
sudo -H pip3 install grpcio-tools

