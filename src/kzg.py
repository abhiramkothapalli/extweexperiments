#!/usr/bin/env python

'''kzg.py: Implements KZG polynomial commitment scheme'''

from gfec import GF, g1, g2, sampleGF, pair
from polynomial import Polynomial, samplePoly

def setup(t):

    # Create generators for commitment.
    r = sampleGF()
    h = g1 * r

    # Generate secret evaluation point.
    a = sampleGF()

    # Commit to powers of a.
    gp = []
    hp = []

    acc = GF(1)
    for i in range(0, t + 1):
        gp += [g1 * acc]
        hp += [h * acc]
        acc = acc * a

    # Generate public key and secret key.
    pk = (t, gp, hp, g2, g2 * a)
    sk = a

    return (pk, sk)

 
def commit(pk, f, r=None):

    t, gp, hp, g2, g2a = pk

    if not isinstance(r, Polynomial):
        r = samplePoly(t + 1)

    fc = f.coeffs()
    rc = r.coeffs()

    cg = gp[0] * fc[0]
    ch = hp[0] * rc[0]
    for i in range(1, len(fc)):
        cg = cg + (gp[i] * fc[i])
        ch = ch + (hp[i] * rc[i])

    com = cg + ch
    
    return com, r

def open_poly(pk, com, f, r):
    return (f, r)

def verify_poly(pk, com, f, r):
    return commit(pk, f, r)[0] == com

def open_eval(pk, f, u, r):

    x = Polynomial([GF(0), GF(1)])
    fu = f(u)
    ru = r(u)
    
    fp = (f - fu) / (x - u)
    rp = (r - ru) / (x - u)

    w = commit(pk, fp, rp)[0]

    return (u, fu, ru, w)

def verify_eval(pk, com, pi):

    t, gp, hp, g2, g2a = pk
    u, fu, ru, w = pi

    g = gp[0]
    h = hp[0]
    
    return pair(com, g2) == pair(w, g2a - g2 * u) * pair(g * fu + h * ru, g2)


if __name__ == '__main__':

    t = 5

    # Setup
    pk, sk = setup(t)

    # Create random polynomial
    # TODO: does not work for lower degree poly
    f = samplePoly(t + 1)

    # Commit to polynomial
    com, r = commit(pk, f)

    # Open the polynomial
    f, r = open_poly(pk, com, f, r)

    # Verify polynomial opening
    assert verify_poly(pk, com, f, r)

    # Pick random evaluation point
    u = sampleGF()

    # Evaluate and prove f(u)
    pi = open_eval(pk, f, u, r)

    # Verify the proof
    assert verify_eval(pk, com, pi)



