cd /local/repository

sudo apt update
sudo apt --assume-yes install python3-pip
pip3 install Pyro4

sudo apt-get --assume-yes install libgmp-dev
make

pyro4-ns -p $1 &

# Wait for nodes to start
# sleep 20

#cd network
#python3 bulletin.py
