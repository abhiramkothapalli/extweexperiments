from concurrent import futures
import time
import timeit
import math
import logging
import argparse

#from addr_config import *

import grpc

# Import the generated classes
import services_pb2       # Messages
import services_pb2_grpc  # Services

def timer(func):
    def wrapper(*args, **kwargs):
        number = 1
        result = timeit.timeit(lambda: func(*args, *kwargs), number=number)
        name = str(func.__name__)
        print(name + ": " +  str(result / float(number)))
        return result
    return wrapper

class AddrConfig():
    def __init__(self, king_addr, old_addrs, new_addrs):
        self.king_addr = king_addr
        self.old_addrs = old_addrs
        self.new_addrs = new_addrs

class BulletinBoard():
    def __init__(self, addr_config):
        self.addr_config = addr_config
        
        # Establish connections to new nodes
        self.new_nodes = []
        for addr in addr_config.new_addrs:
            channel = grpc.insecure_channel(addr)
            self.new_nodes.append(services_pb2_grpc.NodeServiceStub(channel))

    @timer
    def refresh(self):
        logging.info("Refresh: Begin")
        # Send a request to each node in the new committee
        empty = services_pb2.EmptyMsg()
        futures = []
        for node in self.new_nodes:
            futures.append(node.StartRefresh.future(empty))

        # Wait for responses
        for future in futures:
            response = future.result()
        
        logging.info("Refresh: End")


if __name__ == '__main__':

    N = 64
    
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Node")
    parser.add_argument('-a', '--addr', action='store', required=True, 
        help="This node's IP/hostname:port")
    parser.add_argument('-k', '--king', action='store', required=True, 
        help="The king's IP/hostname:port")
    # parser.add_argument('-o', '--old', action='append', required=True, 
    #     help="An old committee IP/hostname:port")
    # parser.add_argument('-n', '--new', action='append', required=True, 
    #     help="A new committee IP/hostname:port")
    args = parser.parse_args()

    old_nodes = ['node' + str(n) + ':' + '50050' for n in range(N)]
    new_nodes = ['node' + str(N + n) +  ':' + '50050' for n in range(N)]

    config = AddrConfig(args.king, old_nodes, new_nodes)

    board = BulletinBoard(config)
    board.refresh()
