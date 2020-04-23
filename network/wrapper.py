import Pyro4
import pickle
import sys
import base64
import time


sys.excepthook = Pyro4.util.excepthook

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Wrapper():


    def __init__(self, u, n):
        self.u = u
        self.n = n

    def get_node(self, u):
        i, j = u
        # TODO: This is hardcoded
        #ns = Pyro4.locateNS(host='bulletin', port=9090)
        ns = Pyro4.locateNS(host='localhost', port=9090)
        uri = ns.lookup(str(i) + str(j))
        node = Pyro4.Proxy(uri)
        return node

    def get_old_nodes(self):
        nodes = [self.get_node((0, j)) for j in range(self.n)]

        for n in nodes:
            n._pyroAsync()

        return nodes

    def get_new_nodes(self):
        nodes = [self.get_node((1, j)) for j in range(self.n)]

        for n in nodes:
            n._pyroAsync()

        return nodes

    def wrap(self, m):
        c = pickle.dumps(m, protocol=0).decode('utf-8')
        return c

    def unwrap(self, c):
        m = pickle.loads(c.encode('utf-8'))
        return m
