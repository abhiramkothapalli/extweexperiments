import Pyro4
import pickle
import sys

sys.excepthook = Pyro4.util.excepthook

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Wrapper():

    def __init__(self, u, NSHOST, NSPORT):

        self.u = u
        self.NSHOST = NSHOST
        self.NSPORT = NSPORT

    def set_params(self, params):

        n, pk = self.unwrap(params)
        
        self.n = n
        self.pk = pk

    def get_node(self, u):
        i, j = u
        ns = Pyro4.locateNS(host=self.NSHOST, port=self.NSPORT)
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
