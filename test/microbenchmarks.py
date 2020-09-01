#!/usr/bin/env python

import sys
sys.path.append('../src/')

import time
from gfec import sampleGF, g1, g2, pair
import kzg
from polynomial import samplePoly
from interpolation import interpolate

import numpy as np


''' Micro Benchmarks'''

import timeit

N = 500

def microtimer(func):
    def wrapper(*args, **kwargs):
        results = timeit.repeat(lambda: func(*args, *kwargs), number=1, repeat=N)

        name = str(func.__name__)
        U = np.max(results)
        L = np.min(results)
        median = np.median(results)
        mean = np.mean(results)
        std = np.std(results)
        
        ret = [name, U, L, median, mean, std]

        print(name + ": " +  str(ret[5]/ret[4]))
        return ret
    return wrapper


''' Field and Curve Operations '''


@microtimer
def gf_add(a, b):
    return a + b

@microtimer
def gf_multiply(a, b):
    return a * b

@microtimer
def gf_div(a, b):
    return a / b

@microtimer
def ec_add(A, B):
    return A + B

@microtimer
def ec_scalar_mult(a, B):
    return B * a

@microtimer
def ec_pair(A, B):
    return pair(A, B)

@microtimer
def ec2_add(A, B):
    return A + B

@microtimer
def ec2_scalar_mult(a, B):
    return B * a




''' KZG '''

@microtimer
def kzg_setup(d):
    return kzg.setup(d)[0]

@microtimer
def kzg_commit(pk, f):
    return kzg.commit(pk, f)

@microtimer
def kzg_eval(pk, f, u, r):
    return kzg.open_eval(pk, f, u, r)

@microtimer
def kzg_verify(pk, com, pi):
    return kzg.verify_eval(pk, com, pi)

@microtimer
def polynomial_interpolate(X, Y):
    return interpolate(X, [Y])
    

def benchmark_kzg(d):

    runtimes = []

    # Setup One run first
    pk = kzg.setup(d)[0]
    f = samplePoly(d + 1)
    com, r = kzg.commit(pk, f)
    u = sampleGF()
    pi = kzg.open_eval(pk, f, u, r)
    kzg.verify_eval(pk, com, pi)

    runtimes += [kzg_setup(d)]
    runtimes += [kzg_commit(pk, f)]
    runtimes += [kzg_eval(pk, f, u, r)]
    runtimes += [kzg_verify(pk, com, pi)]

    return runtimes

def benchmark_polynomial(d):


    X = [sampleGF() for i in range(0, d + 1)]
    Y = [sampleGF() for i in range(0, d + 1)]

    return polynomial_interpolate(X, Y)

if __name__ == '__main__':


    ''' Field Operations '''


    filename = 'fop_results.txt'

    f = open(filename, 'w+')


    a = sampleGF()
    b = sampleGF()

    f.write(str(gf_add(a, b)) + '\n')
    f.write(str(gf_multiply(a, b)) + '\n')
    f.write(str(gf_div(a, b)) + '\n')

    A1 = g1 * a
    B1 = g1 * b
    A2 = g2 * a
    B2 = g2 * b

    f.write(str(ec_add(A1, B1)) + '\n')
    f.write(str(ec_scalar_mult(a, B1)) + '\n')

    f.write(str(ec2_add(A2, B2)) + '\n')
    f.write(str(ec2_scalar_mult(a, B2)) + '\n')

    f.write(str(ec_pair(A1, B2)) + '\n')

    f.close()

    filename = 'kzg_results.txt'



    '''KZG'''
    
    f = open(filename, 'w+')

    for d in [16, 32, 64]:

        runtimes = benchmark_kzg(d)

        f.write('DEGREE: ' + str(d) + '\n')

        for runtime in runtimes:
            f.write(str(runtime) + '\n')

        poly = benchmark_polynomial(d)
        f.write(str(poly) + '\n')

    f.close()
    
    
    

    



    

    

    





    

    
