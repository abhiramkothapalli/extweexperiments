#!/usr/bin/env python

''' benchmarking.py benchmarks various dpss routines '''

import sys
sys.path.append('../src/')

import time

#import dpss
from dpss import *
import vss
import kzg
from gfec import sampleGF, g1, g2, pair
from polynomial import samplePoly
from interpolation import interpolate
import polynomial

tracefile = 'tracefile.txt'

def timer(func, runtimes, key):
    """
    A timer decorator
    """
    def wrapper(*args, **kwargs):
        """
        A nested function for timing other functions
        """
        res = None

        start = time.process_time()
        res = func(*args, **kwargs) # Take last result
        end = time.process_time()
        
        runtime = end - start

        if key not in runtimes:
            runtimes[key] = []

        runtimes[key] += [runtime]

        print(key + ': ' + str(runtime))
        open(tracefile, 'a+').write(str(key) + ', ' + str(runtime) + '\n')
        return res
    return wrapper

def run_dpss(n, t):


    runtimes = {}
    T = lambda func, key: timer(func, runtimes, key)

    ''' Setup '''

    # Create public key.
    pk = T(setup, 'setup')(n, t)


    ''' Create Session Key '''

    # Each party computes verified shares.
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

    # Sanity Check
    assert s == secret
    return runtimes

def export(table, fname):

    f = open(fname, 'w')

    for row in table:
        for c in row:
            f.write(str(c) + ', ')
        f.write('\n')


def run_experiment(n):

    t = int(n/2)

    runtimes = run_dpss(n, t)

    arts = {}

    # Average runtimes
    for k in runtimes:
        arts[k] = sum(runtimes[k]) / len(runtimes[k])

    nrts = {}

    nrts['setup'] = arts['setup']

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

    f = open(tracefile, 'a+')

    print('TOTALS: ' + str(n))
    f.write('TOTALS: ' + str(n) + '\n')
    

    for k in nrts:
        print(str(k) + ': ' + str(nrts[k]))


    for k in nrts:
        f.write(str(k) + ', ' + str(nrts[k]) + '\n')
    f.close()

    return nrts



    

if __name__ == '__main__':

    filename = 'benchmarking_results.txt'

    N = [4, 8, 16] # CONFIGURE 
    runs = 2
    

    for n in N:

        nrts = run_experiment(n)

        f=open(filename, "a+")
        f.write(str(n) + ', ')
        f.write(str(nrts['setup']) + ', ')
        f.write(str(nrts['setup_sharing_randomness']) + ', ')
        f.write(str(nrts['old_setup_refresh_randomness']) + ', ')
        f.write(str(nrts['new_setup_refresh_randomness']) + ', ')
        f.write(str(nrts['client_share']) + ', ')
        f.write(str(nrts['node_receive_share']) + ', ')
        f.write(str(nrts['refresh']) + ', ')
        f.write(str(nrts['refresh_king']) + ', ')
        f.write(str(nrts['reconstruct']) + ', ')
        f.write('\n')
        f.close()
        
        


    
    
    






    
