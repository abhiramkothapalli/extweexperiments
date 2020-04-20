#!/usr/bin/env python

'''dpss.py: Implements the DPSS protocol.'''

from polynomial import Polynomial
from interpolation import interpolate
from gfec import GF, sampleGF
import vss


''' Helper Methods '''

def gen_vandermonde(n, t):

    m = n - t
    la = [GF(a) for a in range(2, m + 2)]
    #V = [[a ** i in range(0, n)] for a in la]

    V = []

    for a in la:
        v = []
        at = GF(1)
        for i in range(0, n):
            v += [at]
            at = at * a
        V += [v]
        

    return V

''' DPSS Psueudorandomness '''

def gen_rand(pk, s):

    V = pk['V']

    R = []
    for i in range(0, len(V)):
        R += [s[0] * V[i][0]]
        for j in range(1, len(V[0])):
            R[i] += s[j] * V[i][j]
            
    return R


def challenge(elems):

    # TODO: Fill in correct challenge method.
    pts = eval_points(len(elems))
    C = interpolate(pts, [elems])[0]

    return C(0)


''' Distribution '''

def _transform(p1, p2, c):
    p = [val for pair in zip(p1, p2) for val in pair]
    P = Polynomial(p)
    return P(c)

def _verification_dist(ss, coms, gss, gcoms, c):

    ns = _transform(gss, ss, c)
    ncom = _transform(gcoms, coms, c)


    return ns, ncom

def distribution(pk):

    kvss = pk['vss']

    s = sampleGF()
    r = sampleGF()

    ss, C = vss.share(kvss, s, r)
    sst, Ct = vss.share(kvss, s, r)

    return (ss, C), (sst, Ct)


def verification_dist(ss, coms, gss, gcoms, comst, gcomst, c):

    # Old and new committee run the same code.
    ns, ncom = _verification_dist(ss, coms, gss, gcoms, c)
    ncomt = _transform(gcomst, comst, c)

    return ns, ncom, ncomt

def _check_commit(pk, ss, com):

    kvss = pk['vss']


    u, v, Pu, Pv = vss.reconstruct_full(kvss, (ss, com))

    ncom = vss.commit(kvss, Pu, Pv)

    return com == ncom

def single_veri_compute(s, com, gs, gcom, comt, gcomt, c):

    # The input is specific for party in question P'_i
    
    ns = gs + s * c
    ncom = gcom + com * c
    ncomt = gcomt + comt * c
    
    return ns, ncom, ncomt


def single_veri_check(pk, ss, com, sst, comt):

    com_valid = _check_commit(pk, ss, com)
    comt_valid = _check_commit(pk, sst, comt)

    kvss = pk['vss']

    u, v = vss.reconstruct(kvss, (ss, com))
    ut, vt = vss.reconstruct(kvss, (sst, comt))

    return com_valid and comt_valid and (u == ut) and (v == vt)

def verification_check(pk, pis, com, pist, comt):
    
    return single_veri_check(pk, pis, com, pist, comt)

''' Output '''

def _output(pk, ps, coms):

    rps = gen_rand(pk, ps)
    rcoms = gen_rand(pk, coms)

    return rps, rcoms

def output(pk, pis, coms, comst):

    pisr, comsr = _output(pk, pis, coms)
    comst = gen_rand(pk, coms)

    return pisr, comsr, comst


''' Refresh '''

def refresh_preprocessing(ss, scom, sr, rcom):

    return (ss + sr), (scom + rcom)

def refresh_king(pk, ss, com):

    # Note: com = scom + rcom

    kvss = pk['vss']
    
    # TODO: maybe can calculate witness the same way in linear.
    u, v, Pu, Pv = vss.reconstruct_full(kvss, (ss, com))

    return vss.create_share(kvss, Pu, GF(0), Pv)

def refresh_postprocessing(pk, kpi, kcom, spi, scom):

    # Check correctness of the reconstruction

    kvss = pk['vss']

    if not kpi.i == GF(0):
        raise Exception('Kings reconstruction is not at zero point')

    if not vss.verify(kvss, kpi, kcom):
        raise Exception('Kings reconstruction did not verify')

    # Calculate new commitment and witness for Kings reconstruction.
    Pu = Polynomial([kpi.u])
    Pv = Polynomial([kpi.v])
    npi = vss.create_share(kvss, Pu, spi.i, Pv)
    nc = vss.commit(kvss, Pu, Pv)

    pi = npi - spi
    com = nc - scom
    
    return pi, com


''' Setup '''


def setup_dist(pk):

    kvss = pk['vss']

    return vss.share(kvss)

def setup_verification_dist(pis, coms, gpis, gcoms, c):

    return _verification_dist(pis, coms, gpis, gcoms, c)

def setup_verification_check(pk, ss, com):

    return _check_commit(pk, ss, com)
 
def setup_single_veri_compute(s, com, gs, gcom, c):

    ns = gs + s * c
    ncom = gcom + com * c

    return ns, ncom

def setup_single_veri_check(pk, ss, com):

    return _check_commit(pk, ss, com)

def setup_output(pk, ss, coms):

    return _output(pk, ss, coms)

def setup_fresh_client(pk, rs, com, s):

    kvss = pk['vss']

    r, u = vss.reconstruct(kvss, (rs, com))

    # Randomly sample z.
    z = sampleGF()

    # Return items to publish.
    sr = s + r
    zu = z + u

    return sr, zu

def setup_fresh_parties(pk, u, v, ss, com):

    kvss = pk['vss']

    # Compute the commitment for u, v.
    Pu = Polynomial([u])
    Pv = Polynomial([v])
    npi = vss.create_share(kvss, Pu, ss.i, Pv)
    nc = vss.commit(kvss, Pu, Pv)

    pi = npi - ss
    c = nc - com
    
    return pi, c

''' Main '''

def setup(n, t):

    key = {}

    key['vss'] = vss.setup(n, t)
    key['V'] = gen_vandermonde(n, t)
    
    return key

def share(pk, ek, s):

    rs, com = ek

    return setup_fresh_client(pk, rs, com, s)

def reconstruct(pk, shares):

    kvss = pk['vss']

    s, r = vss.reconstruct(kvss, shares)
    return s


if __name__ == '__main__':

    ''' Environment Parameters '''

    # Number of parties and threshold.
    n = 2
    t = 1

    ''' Setup '''

    # Create public key.
    pk = setup(n, t)

    ''' Create Session Key '''

    # Each party computes verified shares.
    sss = [setup_dist(pk) for i in range(0, n)]

    # Verify the setup distribution
    gsss = [setup_dist(pk) for i in range(0, n)]
    c = sampleGF() # TODO: test this correctly
    nss = []
    ncoms = []
    for i in range(0, n):
        ss = [share[0][i] for share in sss]
        coms = [share[1] for share in sss]
        gss = [share[0][i] for share in gsss]
        gcoms = [share[1] for share in gsss]
        ns, ncom = setup_verification_dist(ss, coms, gss, gcoms, c)
        nss += [ns]
        ncoms += [ncom]
    assert setup_verification_check(pk, nss, ncoms[0])


    # Single verify the setup distribution
    c = sampleGF()
    for i in range(0, n):
        nss = []
        ncoms = []
        for j in range(0, n):
            s = sss[i][0][j]
            com = sss[i][1]
            gs = gsss[i][0][j]
            gcom = gsss[i][1]
            ns, ncom = setup_single_veri_compute(s, com, gs, gcom, c)
            nss += [ns]
            ncoms += [ncom]
        ncom = ncoms[0]
        assert setup_single_veri_check(pk, nss, ncom)


    # Each party aggregates verified shares.
    coms = [share[1] for share in sss]
    rss = []
    rcomss = []
    for i in range(0, n):
        ss = [share[0][i] for share in sss]
        rs, rcoms = setup_output(pk, ss, coms)
        rss += [rs]
        rcomss += [rcoms]

    
    # # Verify commitments are valid.
    # # Pick one set of commitments.
    # rcoms = rcomss[0]
    # for i in range(0, n):
    #     for j in range(0, n - t):
    #         e = rss[i][j]
    #         pi = e.i, e.u, e.v, e.w
    #         assert verify_eval(pk[1], rcoms[j], pi)


    # Pick out a single session key
    k = 0
    rs = [rs[k] for rs in rss]
    com = rcomss[0][k]
    ek = (rs, com)

    # # Check session key
    # for i in range(0, n):
    #     e = rs[i]
    #     pi = e.i, e.u, e.v, e.w
    #     assert verify_eval(pk[1], com, pi)


    ''' Create Refresh Key '''

    # Each party computes verified shares
    sss = [distribution(pk) for i in range(0, n)]

    # Calculate commitments
    coms = [e[0][1] for e in sss]
    comst = [e[1][1] for e in sss]


    # Old parties aggregate shares
    orss = []
    orcomss = []
    orcomtss = []
    for i in range(0, n):
        ss = [e[0][0][i] for e in sss]
        rs, rcoms, rcomst = output(pk, ss, coms, comst)
        orss += [rs]
        orcomss += [rcoms]
        orcomtss += [rcomst]

    # New parties aggregate shares
    nrss = []
    nrcomss = []
    nrcomtss = []
    for i in range(0, n):
        ss = [e[1][0][i] for e in sss]
        rs, rcomst, rcoms = output(pk, ss, comst, coms)
        nrss += [rs]
        nrcomss += [rcoms]
        nrcomtss += [rcomst]


    # # Verify old shares are valid.
    # # Pick one set of commitments.
    # orcoms = orcomss[0]
    # for i in range(0, n):
    #     for j in range(0, n - t):
    #         e = orss[i][j]
    #         pi = e.i, e.u, e.v, e.w
    #         assert verify_eval(pk[1], orcoms[j], pi)

    # # Verify new shares are valid.
    # # Pick one set of commitments.
    # nrcoms = nrcomss[0]
    # for i in range(0, n):
    #     for j in range(0, n - t):
    #         e = nrss[i][j]
    #         pi = e.i, e.u, e.v, e.w
    #         assert verify_eval(pk[1], nrcoms[j], pi)

    # Pick out single refresh key
    k = 0
    ors = [rs[k] for rs in orss]
    ocom = orcomss[0][k]
    nrs = [rs[k] for rs in nrss]
    ncomr = nrcomss[0][k]

    # # Check old refresh key
    # for i in range(0, n):
    #     e = ors[i]
    #     pi = e.i, e.u, e.v, e.w
    #     assert verify_eval(pk[1], ocom, pi)

    # # Check new refresh key
    # for i in range(0, n):
    #     e = nrs[i]
    #     pi = e.i, e.u, e.v, e.w
    #     assert verify_eval(pk[1], ncomr, pi)


    # Check consistencies between old and new refresh keys.
    #abc, ghi, V = pk
    abc = pk['vss']
    ghi = pk['V']
    ro, so, Pro, Pso = vss.reconstruct_full(abc, (ors, ocom))
    rn, sn, Prn, Psn = vss.reconstruct_full(abc, (nrs, ncomr))
    assert ro == rn and so == sn


    # Verify the distribution
    c = sampleGF()
    gsss = [distribution(pk) for i in range(0, n)]

    # Calculate commitments
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

        ns, ncom, ncomt = verification_dist(ss, coms, gss, gcoms, comst, gcomst, c)
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

        ns, ncomt, ncom = verification_dist(sst, comst, gsst, gcomst, coms, gcoms, c)
        nnss += [ns]
        nncomss += [ncom]
        nncomtss += [ncomt]

    com = oncomss[0]
    comt = oncomtss[0]

    assert verification_check(pk, onss, com, nnss, comt)


    # Single Verify the distribution.
    c = sampleGF()
    for i in range(0, n):
        nss = []
        oncoms = []
        nncoms = []
        nsst = []
        oncomst = []
        nncomst = []
        for j in range(0, n):

            s = sss[i][0][0][j]
            com = sss[i][0][1]
            gs = gsss[i][0][0][j]
            gcom = gsss[i][0][1]

            st = sss[i][1][0][j]
            comt = sss[i][1][1]
            gst = gsss[i][1][0][j]
            gcomt = gsss[i][1][1]


            # Old Committee
            ns, ncom, ncomt = single_veri_compute(s, com, gs, gcom, comt, gcomt, c)
            nss += [ns]
            oncoms += [ncom]
            oncomst += [ncomt]

            # New Committee
            ns, ncomt, ncom = single_veri_compute(st, comt, gst, gcomt, com, gcom, c)
            nsst += [ns]
            nncoms += [ncom]
            nncomst += [ncomt]

        ncom = oncoms[0]
        ncomt = oncomst[0]
        assert single_veri_check(pk, nss, ncom, nsst, ncomt)

    

    ''' Share '''

    # Sample random secret
    secret = sampleGF()

    # Create sharing from pk and session key
    sr, zu = share(pk, ek, secret)

    # Parties handle secret
    rs, com = ek
    ss = []
    coms = []
    for i in range(0, n):
        pi, c = setup_fresh_parties(pk, sr, zu, rs[i], com)
        ss += [pi]
        coms += [c]

    # # Verify shares
    # com = coms[0]
    # for s in ss:
    #     pi = s.i, s.u, s.v, s.w
    #     assert verify_eval(pk[1], com, pi)

    
    # # Check reconstruction before refresh
    # com = coms[0]
    # s = reconstruct(pk, (ss, com))
    # assert s == secret



    ''' Refresh '''

    # Old parties preprocess
    scom = coms[0]
    pksss = []
    pkcoms = []
    for i in range(0, n):
        pkss, pkcom = refresh_preprocessing(ss[i], scom, ors[i], ocom)
        pksss += [pkss]
        pkcoms += [pkcom]

    # King reconstructs from parties shares
    kpi = refresh_king(pk, pksss, pkcoms[0])
    kcom = pkcoms[0]

    # # Check kings result.
    # pi = kpi.i, kpi.u, kpi.v, kpi.w
    # assert verify_eval(pk[1], kcom, pi)

    # New parties postprocess
    scom = coms[0]
    nss = []
    ncoms = []
    for i in range(0, n):
        ns, ncom = refresh_postprocessing(pk, kpi, kcom, nrs[i], ncomr)
        nss += [ns]
        ncoms += [ncom]

    # # Check shares are valid
    # ncom = ncoms[0]
    # for i in range(0, n):
    #     e = nss[i]
    #     pi = e.i, e.u, e.v, e.w
    #     assert verify_eval(pk[1], ncom, pi)

        
    ''' Reconstruct '''
    ncom = ncoms[0]
    s = reconstruct(pk, (nss, ncom))
    assert s == secret

    
        

        


    
        
        

    
    

    

            


    
    
        
    

    
    

    
        
        

    



    
    
