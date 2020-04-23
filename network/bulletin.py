import sys
sys.path.append('../src/')

import Pyro4
from node import Node
from client import Client
import dpss
import time
from gfec import sampleGF
import pickle
import params
import os
import create_network

def wrap(m):
    c = pickle.dumps(m, protocol=0).decode('utf-8')
    return c

def unwrap(c):
    m = pickle.loads(c.encode('utf-8'))
    return m

def create_client(n, pk):

    ''' Create a client '''

    client_id = (2, 0)
    
    return Client(client_id, n, pk)

def generate_setup_randomness(nodes, new_nodes):

    ''' Setup Randomness Distribution and Verification '''

    results = [n.generate_setup_randomness() for n in nodes]
    [r.value for r in results]

def generate_refresh_randomness(nodes, new_nodes):

    ''' Refresh Randomness Distribution and Verification '''

    results = [n.generate_refresh_randomness() for n in nodes + new_nodes]
    [r.value for r in results]


def refresh(nodes, new_nodes):

    ''' Refresh '''

    results = [n.refresh() for n in new_nodes]
    [r.wait() for r in results]

def get_nodes(n, pk):

    nodes = [Pyro4.Proxy("PYRONAME:" + str(0) + str(i)) for i in range(n)]
    new_nodes = [Pyro4.Proxy("PYRONAME:" + str(1) + str(i)) for i in range(n)]


    ''' Setup Environment '''
    
    for node in nodes:
        node.flush()
        node.set_params(wrap((n, pk)))
    for node in new_nodes:
        node.flush()
        node.set_params(wrap((n, pk)))

    # Make all nodes async
    for node in nodes:
        node._pyroAsync()
    for node in new_nodes:
        node._pyroAsync()

    return nodes, new_nodes




def run_experiment(n, t, pk):

    nodes, new_nodes = get_nodes(n, pk)

    ''' Setup '''

    generate_setup_randomness(nodes, new_nodes)
    generate_refresh_randomness(nodes, new_nodes)

    ''' Share '''

    client = create_client(n, pk)
    secret = sampleGF()
    start = time.time()
    client.share(secret)
    end = time.time()
    share_time = end - start


    ''' Refresh '''

    start = time.time()
    refresh(nodes, new_nodes)
    end = time.time()
    refresh_time = end - start


    ''' Reconstruct '''

    new_client = create_client(n, pk)
    start = time.time()
    reconst_secret = new_client.reconstruct()
    end = time.time()
    reconst_time = end - start


    ''' Sanity Check '''

    assert secret == reconst_secret
    return (share_time, refresh_time, reconst_time)

if __name__ == '__main__':

    N = params.N
    T = params.T
    PK = params.PK

    Pyro4.config.THREADPOOL_SIZE = 1024


    for i in range(len(N)):

        print('Starting Experiment: ' + str(N[i]) + ' ' + str(T[i]))
        results = run_experiment(N[i], T[i], PK[i])
        print(results)

    
        

    
