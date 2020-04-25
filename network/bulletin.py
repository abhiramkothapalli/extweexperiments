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
import timeit


def timer(func):
    def wrapper(*args, **kwargs):
        result = timeit.timeit(lambda: func(*args, *kwargs), number=1)
        name = str(func.__name__)
        print(name + ": " +  str(result))
        return result
    return wrapper

def wrap(m):
    c = pickle.dumps(m, protocol=0).decode('utf-8')
    return c

def unwrap(c):
    m = pickle.loads(c.encode('utf-8'))
    return m

def create_client(n, pk, NSHOST, NSPORT):

    ''' Create a client '''

    client = Client(None, NSHOST, NSPORT)
    client.initalize(wrap((n, pk)))
    return client

@timer
def generate_setup_randomness(nodes, new_nodes):

    ''' Setup Randomness Distribution and Verification '''

    results = [n.generate_setup_randomness() for n in nodes]
    [r.wait() for r in results]

@timer
def generate_refresh_randomness(nodes, new_nodes):

    ''' Refresh Randomness Distribution and Verification '''


    results = [n.generate_refresh_randomness() for n in nodes + new_nodes]
    [r.wait() for r in results]

@timer
def refresh(nodes, new_nodes):

    ''' Refresh '''

    results = [n.refresh() for n in new_nodes]
    [r.wait() for r in results]


def get_nodes(n, pk):

    nodes = [Pyro4.Proxy("PYRONAME:" + str(0) + str(i)) for i in range(n)]
    new_nodes = [Pyro4.Proxy("PYRONAME:" + str(1) + str(i)) for i in range(n)]

    # Make all nodes async
    for node in nodes + new_nodes:
        node._pyroAsync()

    ''' Setup Environment '''

    request_inits = [node.initalize(wrap((n, pk))) for node in nodes + new_nodes]
    [r.wait() for r in request_inits]

    return nodes, new_nodes

@timer
def client_share(client, secret):
    client.share(secret)

@timer
def client_reconstruct(client):
    client.reconstruct()

def run_experiment(n, t, pk):

    nodes, new_nodes = get_nodes(n, pk)

    ''' Setup '''

    setup_randomness_time = generate_setup_randomness(nodes, new_nodes)
    refresh_randomness_time = generate_refresh_randomness(nodes, new_nodes)

    ''' Share '''

    client = create_client(n, pk, params.NSHOST, params.NSPORT)
    secret = sampleGF()
    client_share_time = client_share(client, secret)
    
    ''' Refresh '''

    refresh_time = refresh(nodes, new_nodes)

    ''' Reconstruct '''

    new_client = create_client(n, pk, params.NSHOST, params.NSPORT)
    client_reconstruct_time = client_reconstruct(new_client)

    return (setup_randomness_time, refresh_randomness_time, client_share_time, refresh_time, client_reconstruct_time)

if __name__ == '__main__':

    N = params.N
    T = params.T
    R = params.R
    PK = params.PK

    resultsfile = params.resultsfile

    Pyro4.config.THREADPOOL_SIZE = params.THREADPOOL_SIZE

    for r in range(R):
        for i in range(len(N)):

            print('Starting Experiment: ' + str(N[i]) + ' ' + str(T[i]))
            results = run_experiment(N[i], T[i], PK[i])
            print(results)


            f = open(resultsfile, 'a+')
            f.write(str(N[i]) + ', ' + str(results)[1:-1] + '\n')
            f.close()

        

    
        

    
