import sys
import Pyro4
from serializer import *

sys.excepthook = Pyro4.util.excepthook


@Pyro4.expose
class Wrapper():

    def __init__(self, u, NSHOST, NSPORT):

        self.u = u
        self.NSHOST = NSHOST
        self.NSPORT = NSPORT


    def flush(self):
        return None

    def setup_network(self, NSHOST, NSPORT):

        with Pyro4.locateNS(host=NSHOST, port=NSPORT) as ns:

            batchns = ns._pyroBatch()

            for i in [0, 1]:
                for j in range(self.n):
                    batchns.lookup(str(i) + str(j))

            results = list(batchns())

            old_nodes = [Pyro4.Proxy(uri) for uri in results[:self.n]]
            new_nodes = [Pyro4.Proxy(uri) for uri in results[self.n:]]

            for nodes in old_nodes + new_nodes:
                nodes._pyroAsync()
                    
            return old_nodes, new_nodes



    def initalize(self, params):

        self.flush()

        n, pk = params
        
        self.n = n
        self.pk = pk

        old_nodes, new_nodes = self.setup_network(self.NSHOST, self.NSPORT)

        self.old_nodes = old_nodes
        self.new_nodes = new_nodes
