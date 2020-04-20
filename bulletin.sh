sudo apt update
sudo apt --assume-yes install python3-pip
pip3 install Pyro4 

Pyro4-ns -p $1 &

# Wait for nodes to start
# sleep 20

#cd network
#python3 bulletin.py
