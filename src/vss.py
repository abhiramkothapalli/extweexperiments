#!/usr/bin/env python

'''vss.py: Implements a verified variant of Shamir's Secret Sharing protocol over GF.'''

from polynomial import samplePoly
from interpolation import interpolate
from gfec import GF, EC1, sampleGF
import kzg

def eval_points(n):
    return [GF(i) for i in range(1, n + 1)]

class Proof():

    def __init__(self, prf):
        self.i, self.u, self.v, self.w = prf

    def __add__(self, o):

        if isinstance(o, Proof):
            if not (self.i == o.i):
                raise Exception('Adding incompatible proofs.')
            nu = self.u + o.u
            nv = self.v + o.v
            nw = self.w + o.w

            prf = self.i, nu, nv, nw

            return Proof(prf)
        else:
            raise NotImplementedError

    __radd__ = __add__

    def __sub__(self, o):

        if isinstance(o, Proof):
            if not (self.i == o.i):
                raise Exception('Adding incompatible proofs.')
            nu = self.u - o.u
            nv = self.v - o.v
            nw = self.w - o.w

            prf = self.i, nu, nv, nw

            return Proof(prf)
        else:
            raise NotImplementedError

    def __mul__(self, o):

        if isinstance(o, GF):
            nu = self.u * o
            nv = self.v * o
            nw = self.w * o

            prf = self.i, nu, nv, nw

            return Proof(prf)
        else:
            raise NotImplementedError

    
    __rmul__ = __mul__


    def __truediv__(self, o):

        if isinstance(o, GF):
            nu = self.u / o
            nv = self.v / o
            nw = self.w / o

            prf = self.i, nu, nv, nw

            return Proof(prf)
        else:
            raise NotImplementedError


    def __str__(self):
        return str((self.i, self.u, self.v, self.w))

    def __getstate__(self):
        return (self.i.__getstate__(),
                self.u.__getstate__(),
                self.v.__getstate__(),
                self.w.__getstate__())


    def __setstate__(self, s):
        self.i = GF()
        self.u = GF()
        self.v = GF()
        self.w = EC1(None) # TODO: Are there any proofs with EC2?

        self.i.__setstate__(s[0])
        self.u.__setstate__(s[1])
        self.v.__setstate__(s[2])
        self.w.__setstate__(s[3])
        
        

def setup(n, t):

    pts = eval_points(n)
    
    key = {}

    key['n'] = n
    key['t'] = t
    # key['B'] = compute_lagrange_basis(pts, GF(0))
    key['com'] = kzg.setup(t)[0]
    
    return key

def create_share(key, U, i, V):

    kcom = key['com']

    return Proof(kzg.open_eval(kcom, U, i, V))

def commit(key, U, V):

    kcom = key['com']

    return kzg.commit(kcom, U, V)[0]

def verify(key, share, C):

    pi = share.i, share.u, share.v, share.w

    kcom = key['com']

    return kzg.verify_eval(kcom, C, pi)



def share(pk, m=None, r=None):

    # TODO this is a weak way to check
    if not isinstance(m, GF):
        m = sampleGF()

    if not isinstance(r, GF):
        r = sampleGF()

    n = pk['n']
    t = pk['t']

    U = samplePoly(t, m)
    V = samplePoly(t, r)

    C = commit(pk, U, V)

    pts = eval_points(n)

    ss = [create_share(pk, U, i, V) for i in pts]

    return (ss, C)


import time

def reconstruct(pk, shares):

    u, v, Pu, Pv = reconstruct_full(pk, shares)

    return u, v


def reconstruct_full(pk, shares):

    ss, C = shares
    t = pk['t']

    ''' Hard check if simple check fails '''



    vss = []
    for s in ss:
        if verify(pk, s, C):
            vss += [s]
        if len(vss) >= t:
            break

    if len(vss) < t:
        raise Exception('Not enough verified shares.')

    X = [s.i for s in vss]
    Yu = [s.u for s in vss]
    Yv = [s.v for s in vss]

    Pu, Pv = interpolate(X, [Yu, Yv])

    return Pu(GF(0)), Pv(GF(0)), Pu, Pv

if __name__ == '__main__':

    # Pick standard threshold.
    n = 64
    t = int(n/2)

    pk = setup(n, t)

    # Pick random secret.
    secret = sampleGF()

    # Create a secret sharing.
    shares = share(pk, secret)

    # Reconstruct the secret from shares.
    start = time.process_time()
    reconst = reconstruct(pk, shares)[0]
    end = time.process_time()

    print(str(n) + " reconstruction time: " + str(end - start))

    # Check validity of reconstruction.
    assert secret == reconst

    u, v, Pu, Pv = reconstruct_full(pk, shares)

    assert Pu(GF(0)) == secret

    

    
