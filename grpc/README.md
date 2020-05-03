
# Setup

python3 -m pip install grpcio
pip3 install grpcio-tools

# Compilation

python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. services.proto

# Run PingPong

python3 ping_server.py  
python3 ping_client.py -s localhost

# Run Dummy Refresh

## Via multiple command lines
python3 node.py -a localhost:50050 -k localhost:50060 -o localhost:50050 -n localhost:50051
python3 node.py -a localhost:50051 -k localhost:50060 -o localhost:50050 -n localhost:50051
python3 node.py -a localhost:50060 -k localhost:50060 -o localhost:50050 -n localhost:50051
python3 bulletin.py -a localhost:50060 -k localhost:50060 -o localhost:50050 -n localhost:50051

## Launch programmatically (only works on localhost)
python3 localtest.py -o 3 -n 3 
