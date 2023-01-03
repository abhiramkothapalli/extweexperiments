import sys
sys.path.append('../src/')

import pickle # Simplifying assumption: In practice we want a more secure serializer

import grpc

# Import the generated classes
import services_pb2       # Messages
import services_pb2_grpc  # Services

def wrap(m):
        c = pickle.dumps(m, protocol=0)
        return services_pb2.Pickle(s=c)

def unwrap(c):
    m = pickle.loads(c.s)
    return m
