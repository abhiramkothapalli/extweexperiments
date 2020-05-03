#cd /local/repository/

echo "Installing Required Packages"

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

# echo "Starting Node"
#cd /local/repository/network
#python3 node.py $1 $2 $3 $4 $5

echo "GRPC"
cd grpc #/local/repository/grpc
pip3 install --upgrade pip
python3 -m pip install grpcio
pip3 install grpcio-tools
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. services.proto

echo "Waiting for ns to start"
sleep 600


python3 node.py -a "node${1}:50050" -k "node0:50050"


