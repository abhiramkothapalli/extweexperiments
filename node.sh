pip3 install Pyro4

# Wait for ns to start
sleep 300 

cd network
python3 node.py $1 $2 $3 $4
