import Pyro4
from node import Node



def create_node(u, daemon, ns, n, pk):

    i, j = u

    node = Node(u, n, pk)
    uri = daemon.register(node)
    ns.register(str(i) + str(j), uri)

    return node

def create_network(n, t, pk):


    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS() # Change for remote test

    for i in range(n):
        [create_node((0, i), daemon, ns, n, pk)]
        [create_node((1, i), daemon, ns, n, pk)]

    daemon.requestLoop()


