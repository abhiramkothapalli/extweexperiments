
# Setup

python3 -m pip install grpcio
pip3 install grpcio-tools

# Compilation

python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. services.proto
