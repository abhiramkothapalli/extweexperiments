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

echo "GRPC"
sudo -H pip3 install --upgrade pip
sudo python3 -m pip install grpcio
sudo -H pip3 install grpcio-tools

echo "Additional"
sudo pip3 install pytz

echo "Building"
sudo make



