import Pyro4
import pickle
import sys

sys.excepthook = Pyro4.util.excepthook


@Pyro4.expose
class Wrapper():


    def __init__(self, u, NSHOST, NSPORT):

        self.u = u
        self.NSHOST = NSHOST
        self.NSPORT = NSPORT

    def flush(self):
        return None

    def get_node(self, u):

        with Pyro4.locateNS(host=self.NSHOST, port=self.NSPORT) as ns:
            uri = ns.lookup(str(u[0]) + str(u[1]))
            node = Pyro4.Proxy(uri)
            return node

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

        n, pk = self.unwrap(params)
        
        self.n = n
        self.pk = pk

        old_nodes, new_nodes = self.setup_network(self.NSHOST, self.NSPORT)

        self.old_nodes = old_nodes
        self.new_nodes = new_nodes



    def wrap(self, m):
        c = pickle.dumps(m, protocol=0).decode('utf-8')
        return c

    def unwrap(self, c):
        m = pickle.loads(c.encode('utf-8'))
        return m
