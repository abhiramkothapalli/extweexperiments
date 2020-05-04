import sys
sys.path.append('../src/')


from node import Node
from client import Client
import dpss
import time
from gfec import sampleGF, g1, g2
import params
import os
import timeit
from serializer import wrap, unwrap

import grpc

# Import the generated classes
import services_pb2       # Messages
import services_pb2_grpc  # Services


def timer(func):
    def wrapper(*args, **kwargs):
        result = timeit.timeit(lambda: func(*args, *kwargs), number=1)
        name = str(func.__name__)
        print(name + ": " +  str(result))
        return result
    return wrapper

def create_client(n, pk, old_addrs, new_addrs):

    ''' Create a client '''

    client = Client(old_addrs, new_addrs)
    client.initalize(wrap((n, pk)))
    return client

@timer
def generate_setup_randomness(old_nodes, new_nodes):

    ''' Setup Randomness Distribution and Verification '''

    results = [n.generate_setup_randomness.future(wrap(None)) for n in old_nodes]
    [r.result() for r in results]

@timer
def generate_refresh_randomness(old_nodes, new_nodes):

    ''' Refresh Randomness Distribution and Verification '''


    future_results = [n.generate_refresh_randomness.future(wrap(None)) for n in old_nodes + new_nodes]
    [r.result() for r in future_results]

@timer
def refresh(old_nodes, new_nodes):

    ''' Refresh '''

    results = [n.refresh.future(wrap(None)) for n in new_nodes]
    [r.result() for r in results]


def get_nodes(old_addrs, new_addrs):

    old_nodes = []
    for addr in params.old_addrs:
        channel = grpc.insecure_channel(addr)
        old_nodes += [services_pb2_grpc.NodeStub(channel)]

    new_nodes = []
    for addr in params.new_addrs:
        channel = grpc.insecure_channel(addr)
        new_nodes += [services_pb2_grpc.NodeStub(channel)]

    return old_nodes, new_nodes



def initalize_nodes(n, pk, old_nodes, new_nodes):

    ''' Setup Environment '''

    future_results = [node.initalize.future(wrap((n, pk))) for node in old_nodes + new_nodes]
    [r.result() for r in future_results]


@timer
def client_share(client, secret):
    client.share(secret)

@timer
def client_reconstruct(client):
    client.reconstruct()

@timer
def ping(node):
    a = sampleGF()
    result = unwrap(node.ping(wrap(a)).result())

def run_experiment(n, t, pk, old_nodes, new_nodes):

    
    ''' Setup '''

    setup_randomness_time = generate_setup_randomness(old_nodes, new_nodes)
    refresh_randomness_time = generate_refresh_randomness(old_nodes, new_nodes)

    ''' Share '''

    client = create_client(n, pk, params.old_addrs, params.new_addrs)
    secret = sampleGF()
    client_share_time = client_share(client, secret)


    ''' Refresh '''

    refresh_time = refresh(old_nodes, new_nodes)

    ''' Reconstruct '''

    new_client = create_client(n, pk, params.old_addrs, params.new_addrs)
    client_reconstruct_time = client_reconstruct(new_client)

    return (setup_randomness_time, refresh_randomness_time, client_share_time, refresh_time, client_reconstruct_time)

if __name__ == '__main__':

    N = params.N
    T = params.T
    R = params.R
    PK = params.PK

    resultsfile = params.resultsfile

    OLD_NODES, NEW_NODES = get_nodes(params.old_addrs, params.new_addrs)


    for r in range(R):
        for i in range(len(N)):

            old_nodes = OLD_NODES[:N[i]]
            new_nodes = NEW_NODES[:N[i]]

            initalize_nodes(N[i], PK[i], old_nodes, new_nodes)

            print('Starting Experiment: ' + str(N[i]) + ' ' + str(T[i]))
            results = run_experiment(N[i], T[i], PK[i], old_nodes, new_nodes)
            print(results)


            f = open(resultsfile, 'a+')
            f.write(str(N[i]) + ', ' + str(results)[1:-1] + '\n')
            f.close()

        

    
        

    
