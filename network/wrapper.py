import sys
from serializer import *

import grpc
import services_pb2       # Messages
import services_pb2_grpc  # Services


class Wrapper(services_pb2_grpc.NodeServicer):

    def __init__(self, old_addrs, new_addrs):
        self._OLDNODES, self._NEWNODES = self.setup_network(old_addrs, new_addrs)
        self.old_addrs = old_addrs
        self.new_addrs = new_addrs

    def flush(self):
        return None

    def setup_network(self, old_addrs, new_addrs):

        old_nodes = []
        new_nodes = []

        for addr in old_addrs:
            channel = grpc.insecure_channel(addr)
            old_nodes += [services_pb2_grpc.NodeStub(channel)]

        for addr in new_addrs:
            channel = grpc.insecure_channel(addr)
            new_nodes += [services_pb2_grpc.NodeStub(channel)]

        return old_nodes, new_nodes



    def initalize(self, request, context=None):

        n, pk = unwrap(request)

        self.flush()

        self.n = n
        self.pk = pk

        self.old_nodes = self._OLDNODES[:n]
        self.new_nodes = self._NEWNODES[:n]

        return wrap(None)




