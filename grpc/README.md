
# Setup

python3 -m pip install grpcio
pip3 install grpcio-tools

# Compilation

python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. services.proto

# Run PingPong

python3 ping_server.py  
python3 ping_client.py -s localhost
