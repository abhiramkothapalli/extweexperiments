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

class NodeServicer(services_pb2_grpc.NodeServiceServicer):
    def __init__(self, addr_config):
        self.addr_config = addr_config

        # Establish connections to everyone else
        channel = grpc.insecure_channel(addr_config.king_addr)
        self.king = services_pb2_grpc.NodeServiceStub(channel)

        self.old_nodes = []
        for addr in addr_config.old_addrs:
            channel = grpc.insecure_channel(addr)
            self.old_nodes.append(services_pb2_grpc.NodeServiceStub(channel))
       
        # Actually, for this test, we don't need connections to the new committee
        self.new_nodes = []
#        for addr in addr_config.new_addrs:
#            channel = grpc.insecure_channel(addr)
#            self.new_nodes.append(services_pb2_grpc.NodeServiceStub(channel))

    # Run on the nodes in the new committee
    def StartRefresh(self, request, context):
        # Reach out to the king
        logging.info("StartRefresh: Begin")
        empty = services_pb2.EmptyMsg()
        response = self.king.GetStuffFromKing(empty)
        logging.info("StartRefresh: End")

        return services_pb2.AckMsg()

    # Run on the king
    def GetStuffFromKing(self, request, context):
        logging.info("GetStuffFromKing: Begin")
        # Send a request to each node in the old committee
        empty = services_pb2.EmptyMsg()
        futures = []
        for node in self.old_nodes:
            futures.append(node.GetOldStuff.future(empty))

        # Wait for responses
        for future in futures:
            response = future.result()

        logging.info("GetStuffFromKing: End")
        return services_pb2.AckMsg()
        
    # Run on the old committee
    def GetOldStuff(self, request, context):
        logging.info("GetOldStuff: Begin + End")
        return services_pb2.AckMsg()


def serve(addr, config):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    services_pb2_grpc.add_NodeServiceServicer_to_server(NodeServicer(config), server)
    print("Starting node on addr %s" % addr)
    server.add_insecure_port(addr)
    server.start()

    # Since server.start() will not block, add a sleep loop 
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

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

    serve(args.addr, config)