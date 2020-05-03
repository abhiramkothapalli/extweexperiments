from concurrent import futures
import time
import math
import logging
import argparse

import grpc

# Import the generated classes
import services_pb2       # Messages
import services_pb2_grpc  # Services

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
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Node")
    parser.add_argument('-a', '--addr', action='store', required=True, 
        help="This node's IP/hostname:port")
    parser.add_argument('-k', '--king', action='store', required=True, 
        help="The king's IP/hostname:port")
    parser.add_argument('-o', '--old', action='append', required=True, 
        help="An old committee IP/hostname:port")
    parser.add_argument('-n', '--new', action='append', required=True, 
        help="A new committee IP/hostname:port")
    args = parser.parse_args()

    config = AddrConfig(args.king, args.old, args.new)

    board = BulletinBoard(config)
    board.refresh()
