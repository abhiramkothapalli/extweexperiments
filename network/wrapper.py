import Pyro4
import pickle
import sys
import base64
import time


sys.excepthook = Pyro4.util.excepthook

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Wrapper():

    buf = {}

    def __init__(self, u, n):
        self.u = u
        self.n = n

        self.flush()

    def get_node(self, u):
        i, j = u
        # TODO: This is hardcoded
        ns = Pyro4.locateNS(host='bulletin', port=9090) 
        uri = ns.lookup(str(i) + str(j))
        node = Pyro4.Proxy(uri)
        return node


    def wrap(self, m):
        c = pickle.dumps(m, protocol=0).decode('utf-8')
        return c

    def unwrap(self, c):
        m = pickle.loads(c.encode('utf-8'))
        return m

    def send(self, j, m):
        #print(str(self.u) + ' -> ' + str(j) + ': '+ str(m))
        c = self.wrap(m)

        node = self.get_node(j)
        node.receive(self.u, c)

    def receive(self, j, c):

        m = self.unwrap(c)

        if j not in self.buf:
            self.buf[j] = []
            
        self.buf[j] += [m]

        #print(str(self.i) + ' <- ' + str(j) + ': '+ str(m))

    def broadcast(self, m, i):

        for j in range(self.n):
            self.send((i, j), m)
            
    def read(self, j):

        if len(self.buf[j]) > 0:
            return self.buf[j].pop(0)
        else:
            raise Exception('Illegal Read')

    def flush(self):
        self.buf = {}
