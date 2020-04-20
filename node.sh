sudo apt update
sudo apt --assume-yes install python3-pip
pip3 install Pyro4

make

# Wait for ns to start
echo "Waiting for ns to start..."
sleep 300
echo "Finished Waiting"

cd network
python3 node.py $1 $2 $3 $4
