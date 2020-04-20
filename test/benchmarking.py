#!/usr/bin/env python

''' benchmarking.py benchmarks various dpss routines '''

import time

#import dpss
from dpss import *
import vss
import kzg
from gfec import sampleGF, g1, g2, pair
from polynomial import samplePoly
from interpolation import interpolate
import polynomial

runs = 1


def timer(func):
    """
    A timer decorator
    """
    def wrapper(*args, **kwargs):
        """
        A nested function for timing other functions
        """
        res = None
        runtimes = []
        for r in range(0, runs):
            start = time.time()
            res = func(*args, **kwargs) # Take last result
            end = time.time()
            runtimes += [end - start]
        
        avg = sum(runtimes) / len(runtimes)
        #print(str(func.__name__) + ': ' + str(avg))
        return avg, res
    return wrapper

''' DPSS Benchmarks '''

@timer
def run_setup(n, t):

    return dpss.setup(n, t)

@timer
def run_share(pk, ek, s):

    return dpss.share(pk, ek, s)

@timer
def run_refresh():

    return None

def run_refresh_king():

    return None
    

@timer
def run_reconstruct(pk, shares):

    return dpss.reconstruct(pk, shares)

@timer
def run_output(pk, ps, cs):

    return dpss._output(pk, ps, cs)

@timer
def run_verification_dist(ss, coms, gss, gcoms, c):

    return dpss._verification_dist(ss, coms, gss, gcoms, c)

@timer
def run_check_commit(pk, ss, com):

    return dpss._check_commit(pk, ss, com)

@timer
def run_kzg_commit(pk, f):

    return kzg.commit(pk, f)

@timer
def run_kzg_open_eval(pk, f, u, r):

    return kzg.open_eval(pk, f, u, r)

@timer
def run_kzg_verify_eval(pk, com, pi):
    
    return kzg.verify_eval(pk, com, pi)

''' Polynomial Benchmarks'''

@timer
def run_polynomial_interpolation(X, Y):

    return polynomial.interpolate(X, Y)


''' Micro Benchmarks'''

@timer
def gf_add(a, b):
    return a + b

@timer
def gf_multiply(a, b):
    return a * b

@timer
def gf_div(a, b):
    return a / b

@timer
def ec_add(A, B):
    return A + B

@timer
def ec_scalar_mult(a, B):
    return B * a

@timer
def ec_pair(A, B):
    return pair(A, B)

@timer
def ec2_add(A, B):
    return A + B

@timer
def ec2_scalar_mult(a, B):
    return B * a


def benchmark_dpss(n, t):

    runtimes = []

    # Benchmark setup
    runtime, pk = run_setup(n, t)
    kvss, kcom, V = pk
    runtimes += [runtime]

    # Create partial shares
    sss = [vss.share((kvss, kcom)) for i in range(0, n)]
    ps = [e[0][0] for e in sss]
    cs = [e[1] for e in sss]

    gsss = [vss.share((kvss, kcom)) for i in range(0, n)]
    gps = [e[0][0] for e in gsss]
    gcs = [e[1] for e in gsss]

    # Create Challenge
    ch = sampleGF()

    # Benchmark sharing
    ss, C = vss.share((kvss, kcom)) # Create random session key
    secret = sampleGF()

    runtime, res = run_share(pk, (ss, C), secret)
    runtimes += [runtime]

    # Benchmark reconstruction
    shares = vss.share((kvss, kcom))
    runtime, res = run_reconstruct(pk, shares)
    runtimes += [runtime]

    # Benchmark output
    runtime, res = run_output(pk, ps, cs)
    runtimes += [runtime]

    # Benchmark verification_dist (_verification_dist)
    runtime, res = run_verification_dist(ps, cs, gps, gcs, ch)
    runtimes += [runtime]

    # Benchmark Commit Check (_check_commit)
    runtime, res = run_check_commit(pk, ss, C)
    runtimes += [runtime]
    

    return runtimes


def new_timer(func, runtimes, key):
    """
    A timer decorator
    """
    def wrapper(*args, **kwargs):
        """
        A nested function for timing other functions
        """
        res = None

        start = time.time()
        res = func(*args, **kwargs) # Take last result
        end = time.time()
        
        runtime = end - start

        if key not in runtimes:
            runtimes[key] = []

        runtimes[key] += [runtime]

        print(key + ': ' + str(runtime))
        return res
    return wrapper

def benchmark_reconstruct(n, t):

    runtimes = {}
    T = lambda func, key: new_timer(func, runtimes, key)

    kvss = vss.setup(n, t)

    # Benchmark reconstruction
    shares = vss.share(kvss)
    res = T(vss.reconstruct_full, 'reconstruct')(kvss, shares)

    return runtimes['reconstruct']

    

def run_dpss_full(n, t):


    runtimes = {}
    T = lambda func, key: new_timer(func, runtimes, key)

    ''' Setup '''

    # Create public key.
    pk = T(setup, 'setup')(n, t)


    ''' Create Session Key '''

    # Each party computes verified shares.
    #sss = [T(setup_dist, (pk)) for i in range(0, n)]
    sss = [T(setup_dist, 'setup_distribution')(pk) for i in range(0, n)]

    # TODO: Each party must verify received shares

    # Verify the setup distribution
    gsss = [T(setup_dist, 'setup_distribution_verification_1')(pk) for i in range(0, n)]
    c = sampleGF() # TODO: test this correctly
    nss = []
    ncoms = []
    for i in range(0, n):
        ss = [share[0][i] for share in sss]
        coms = [share[1] for share in sss]
        gss = [share[0][i] for share in gsss]
        gcoms = [share[1] for share in gsss]
        ns, ncom = T(setup_verification_dist, 'setup_distribution_verification_2')(ss, coms, gss, gcoms, c)
        nss += [ns]
        ncoms += [ncom]
    for i in range(0, n):
        assert T(setup_verification_check, 'setup_distribution_verification_3')(pk, nss, ncoms[i])


    # # Single verify the setup distribution
    # c = sampleGF()
    # for i in range(0, n):
    #     nss = []
    #     ncoms = []
    #     for j in range(0, n):
    #         s = sss[i][0][j]
    #         com = sss[i][1]
    #         gs = gsss[i][0][j]
    #         gcom = gsss[i][1]
    #         # TODO: this measures time to check single party, in practice its * n
    #         ns, ncom = T(setup_single_veri_compute, 'setup_distibution_single_verification_1')(s, com, gs, gcom, c)
    #         nss += [ns]
    #         ncoms += [ncom]
    #     for i in range(0, n):
    #         assert T(setup_single_veri_check, 'setup_distribution_single_verification_2')(pk, nss, ncoms[i])


    # Each party aggregates verified shares.
    coms = [share[1] for share in sss]
    rss = []
    rcomss = []
    for i in range(0, n):
        ss = [share[0][i] for share in sss]
        rs, rcoms = T(setup_output, 'setup_output')(pk, ss, coms)
        rss += [rs]
        rcomss += [rcoms]



    # Pick out a single session key
    k = 0
    rs = [rs[k] for rs in rss]
    com = rcomss[0][k]
    ek = (rs, com)


    ''' Create Refresh Key '''

    # Each party computes verified shares
    sss = [T(distribution, 'distribution')(pk) for i in range(0, n)]

    # Extract commitments
    coms = [e[0][1] for e in sss]
    comst = [e[1][1] for e in sss]


    # Old parties aggregate shares
    orss = []
    orcomss = []
    orcomtss = []
    for i in range(0, n):
        ss = [e[0][0][i] for e in sss]
        rs, rcoms, rcomst = T(output, 'old_output')(pk, ss, coms, comst)
        orss += [rs]
        orcomss += [rcoms]
        orcomtss += [rcomst]

    # New parties aggregate shares
    nrss = []
    nrcomss = []
    nrcomtss = []
    for i in range(0, n):
        ss = [e[1][0][i] for e in sss]
        rs, rcomst, rcoms = T(output, 'new_output')(pk, ss, comst, coms)
        nrss += [rs]
        nrcomss += [rcoms]
        nrcomtss += [rcomst]

    # Pick out single refresh key
    k = 0
    ors = [rs[k] for rs in orss]
    ocom = orcomss[0][k]
    nrs = [rs[k] for rs in nrss]
    ncomr = nrcomss[0][k]


    # Verify the distribution
    c = sampleGF()
    gsss = [T(distribution, 'new_distribution_verification_0')(pk) for i in range(0, n)]

    # Extract commitments
    coms = [share[0][1] for share in sss]
    comst = [share[1][1] for share in sss]
    gcoms = [share[0][1] for share in gsss]
    gcomst = [share[1][1] for share in gsss]


    # Old parties
    onss = []
    oncomss = []
    oncomtss = []
    for i in range(0, n):
        ss = [share[0][0][i] for share in sss]
        gss = [share[0][0][i] for share in gsss]

        ns, ncom, ncomt = T(verification_dist, 'old_distribution_verification_1')(ss, coms, gss, gcoms, comst, gcomst, c)
        onss += [ns]
        oncomss += [ncom]
        oncomtss += [ncomt]

    # New parties
    nnss = []
    nncomss = []
    nncomtss = []
    for i in range(0, n):
        sst = [share[1][0][i] for share in sss]
        gsst = [share[1][0][i] for share in gsss]

        ns, ncomt, ncom = T(verification_dist, 'new_distribution_verification_1')(sst, comst, gsst, gcomst, coms, gcoms, c)
        nnss += [ns]
        nncomss += [ncom]
        nncomtss += [ncomt]

    com = oncomss[0]
    comt = oncomtss[0]

    # Old parties perform checks
    for i in range(0, n):
        com = oncomss[i]
        comt = oncomtss[i]
        assert T(verification_check, 'old_distribution_verification_2')(pk, onss, com, nnss, comt)

    # New parties perform checks
    for i in range(0, n):
        com = nncomss[i]
        comt = nncomtss[i]
        assert T(verification_check, 'new_distribution_verification_2')(pk, onss, com, nnss, comt)


    # # Single Verify the distribution.
    # c = sampleGF()
    # for i in range(0, n):
    #     nss = []
    #     oncoms = []
    #     nncoms = []
    #     nsst = []
    #     oncomst = []
    #     nncomst = []
    #     for j in range(0, n):

    #         s = sss[i][0][0][j]
    #         com = sss[i][0][1]
    #         gs = gsss[i][0][0][j]
    #         gcom = gsss[i][0][1]

    #         st = sss[i][1][0][j]
    #         comt = sss[i][1][1]
    #         gst = gsss[i][1][0][j]
    #         gcomt = gsss[i][1][1]


    #         # Old Committee
    #         # TODO: All this is single time: in practice *n
    #         ns, ncom, ncomt = T(single_veri_compute, 'old_distibution_single_verification_1')(s, com, gs, gcom, comt, gcomt, c)
    #         nss += [ns]
    #         oncoms += [ncom]
    #         oncomst += [ncomt]

    #         # New Committee
    #         ns, ncomt, ncom = T(single_veri_compute, 'new_distribution_single_verification_1')(st, comt, gst, gcomt, com, gcom, c)
    #         nsst += [ns]
    #         nncoms += [ncom]
    #         nncomst += [ncomt]

    #     # Old Party Checks
    #     for i in range(0, n):

    #         ncom = oncoms[i]
    #         ncomt = oncomst[i]
    #         assert T(single_veri_check, 'old_distribution_single_verification_2')(pk, nss, ncom, nsst, ncomt)

    #     # New Party Checks
    #     for i in range(0, n):

    #         ncom = nncoms[i]
    #         ncomt = nncomst[i]
    #         assert T(single_veri_check, 'new_distribution_single_verification_2')(pk, nss, ncom, nsst, ncomt)


    ''' Share '''

    # Sample random secret
    secret = sampleGF()

    # Create sharing from pk and session key
    sr, zu = T(share, 'client_share')(pk, ek, secret)

    # Parties handle secret
    rs, com = ek
    ss = []
    coms = []
    for i in range(0, n):
        pi, c = T(setup_fresh_parties, 'node_share')(pk, sr, zu, rs[i], com)
        ss += [pi]
        coms += [c]


    ''' Refresh '''

    # Old parties preprocess
    scom = coms[0]
    pksss = []
    pkcoms = []
    for i in range(0, n):
        pkss, pkcom = T(refresh_preprocessing, 'refresh_1')(ss[i], scom, ors[i], ocom)
        pksss += [pkss]
        pkcoms += [pkcom]

    # King reconstructs from parties shares
    kpi = T(refresh_king, 'refresh_king')(pk, pksss, pkcoms[0])
    kcom = pkcoms[0]

    # New parties postprocess
    scom = coms[0]
    nss = []
    ncoms = []
    for i in range(0, n):
        ns, ncom = T(refresh_postprocessing, 'refresh_2')(pk, kpi, kcom, nrs[i], ncomr)
        nss += [ns]
        ncoms += [ncom]

        
    ''' Reconstruct '''
    ncom = ncoms[0]
    s = T(reconstruct, 'reconstruct')(pk, (nss, ncom))
    assert s == secret


    return runtimes

    


def benchmark_kzg(kt):

    runtimes = []

    kpk = kzg.setup(kt)[0]
    f = samplePoly(kt + 1)

    # Benchmark kzg commit
    runtime, res = run_kzg_commit(kpk, f)
    com, r = res
    runtimes += [runtime]

    # Benchmark kzg evaluation
    u = sampleGF()
    runtime, res = run_kzg_open_eval(kpk, f, u, r)
    pi = res
    runtimes += [runtime]

    # Benchmark KZG verification
    runtime, res = run_kzg_verify_eval(kpk, com, pi)
    runtimes += [runtime]
    assert res == True

    return runtimes

def benchmark_polynomial(d):


    X = [sampleGF() for i in range(0, d + 1)]
    Y = [sampleGF() for i in range(0, d + 1)]

    runtime, res = run_polynomial_interpolation(X, Y)

    return [runtime]

def export(table, fname):

    f = open(fname, 'w')

    for row in table:
        for c in row:
            f.write(str(c) + ', ')
        f.write('\n')

    



if __name__ == '__main__':

    n = 64
    t = 32

    #runtime = benchmark_reconstruct(n, t)

    runtimes = run_dpss_full(n, t)

    arts = {}

    # Average runtimes
    for k in runtimes:
        arts[k] = sum(runtimes[k]) / len(runtimes[k])

    nrts = {}

    nrts['setup'] = arts['setup']

    # TODO: incorporate single verification
    # TODO: note that this is for n - t randomness

    time_dist = arts['setup_distribution']
    time_dist_verification = arts['setup_distribution_verification_1'] + arts['setup_distribution_verification_2'] + arts['setup_distribution_verification_3']
    time_output = arts['setup_output']

    nrts['setup_sharing_randomness'] = time_dist + time_dist_verification + time_output

    nrts['old_setup_refresh_randomness'] = arts['old_output'] + arts['old_distribution_verification_1'] + arts['old_distribution_verification_2']

    nrts['new_setup_refresh_randomness'] = arts['distribution'] + arts['new_output'] + arts['new_distribution_verification_0'] +  arts['new_distribution_verification_1'] + arts['new_distribution_verification_2']

    nrts['client_share'] = arts['client_share']

    nrts['node_receive_share'] = arts['node_share']

    nrts['refresh'] = arts['refresh_1'] + arts['refresh_2']

    nrts['refresh_king'] = arts['refresh_1'] + arts['refresh_2'] + arts['refresh_king']

    nrts['reconstruct'] = arts['reconstruct']


    print('TOTALS')

    for k in nrts:
        print(str(k) + ': ' + str(nrts[k]))

    exit()
    

    

    tns = [(2, 4), (4, 8), (8, 16), (16, 32), (32, 64)]

    ''' DPSS '''

    dpss_table = [['setup'], ['share'], ['reconstruction'], ['output'], ['verification_dist'], ['check_commit']]

    for tn in tns:
        t, n = tn
        runtimes = benchmark_dpss(n, t)
        for i in range(0, len(dpss_table)):
            dpss_table[i] += [runtimes[i]]

    print(dpss_table)

    export(dpss_table, 'dpss_table.csv')


    ''' KZG '''

    kzg_table = [['commit'], ['evaluation'], ['verification']]

    for tn in tns:
        t, n = tn
        runtimes = benchmark_kzg(t)
        for i in range(0, len(kzg_table)):
            kzg_table[i] += [runtimes[i]]

    print(kzg_table)
    export(kzg_table, 'kzg_table.csv')




    ''' Polynomial '''

    poly_table = [['interpolation']]

    for tn in tns:
        t, n = tn
        runtimes = benchmark_polynomial(t)
        for i in range(0, len(poly_table)):
            poly_table[i] += [runtimes[i]]

    print(poly_table)
    export(poly_table, 'poly_table.csv')





    ''' GFEC '''

    gfec_table = []

    a = sampleGF()
    b = sampleGF()

    runtime, res = gf_add(a, b)
    gfec_table += [['f_add', runtime]]

    
    runtime, res = gf_multiply(a, b)
    gfec_table += [['f_mul', runtime]]
    
    runtime, res = gf_div(a, b)
    gfec_table += [['f_div', runtime]]

    A = g1 * a
    B = g1 * b
    C = g2 * b

    runtime, res = ec_add(A, B)
    gfec_table += [['ec_add', runtime]]

    runtime, res = ec_scalar_mult(a, B)
    gfec_table += [['ec_smul', runtime]]


    A = g2 * a
    B = g2 * b

    runtime, res = ec2_add(A, B)
    gfec_table += [['ec2_add', runtime]]
    
    runtime, res = ec2_scalar_mult(a, B)
    gfec_table += [['ec2_smul', runtime]]

    A = g1 * a
    runtime, res = ec_pair(A, C)
    gfec_table += [['ec_pair', runtime]]

    print(gfec_table)
    export(gfec_table, 'gfec_table.csv')


    


    


    
    
    






    
