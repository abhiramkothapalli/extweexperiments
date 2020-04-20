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

    for n in nodes:
        n.generate_setup_randomness()

def generate_refresh_randomness(nodes, new_nodes):

    ''' Refresh Randomness Distribution and Verification '''


    results_distribution = [n.distribution() for n in new_nodes]
    [r.value for r in results_distribution]


    results_old_verification_1 = [n.old_distribution_verification_1() for n in nodes]
    results_new_verification_1 = [n.new_distribution_verification_1() for n in new_nodes]

    [r.value for r in results_old_verification_1]
    [r.value for r in results_new_verification_1]


    results_old_verification_2 = [n.distribution_verification_2() for n in nodes]
    results_new_verification_2 = [n.distribution_verification_2() for n in new_nodes]
    results_old_output = [n.old_output() for n in nodes]
    results_new_output = [n.new_output() for n in new_nodes]

    [r.value for r in results_old_verification_2]
    [r.value for r in results_new_verification_2]
    [r.value for r in results_old_output]
    [r.value for r in results_new_output]


def refresh(nodes, new_nodes):

    ''' Refresh '''

    king = nodes[0]
    king.refresh_reconstruct().value

    results = [n.refresh() for n in new_nodes]

    [r.wait() for r in results]


def run_experiment(n, t, pk):

    nodes = [Pyro4.Proxy("PYRONAME:" + str(0) + str(i)) for i in range(n)]
    new_nodes = [Pyro4.Proxy("PYRONAME:" + str(1) + str(i)) for i in range(n)]


    ''' Setup Environment '''
    
    for node in nodes:
        node.flush()
        node.set_params(wrap((n, pk)))
    for node in new_nodes:
        node.flush()
        node.set_params(wrap((n, pk)))

    ''' Setup '''

    generate_setup_randomness(nodes, new_nodes) # TODO: Not Async

    # Make all nodes async
    for node in nodes:
        node._pyroAsync()
    for node in new_nodes:
        node._pyroAsync()

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

    
        

    
