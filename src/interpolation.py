#!/usr/bin/env/python

import math
import numpy as np

from gfec import GF, sampleGF
from polynomial import Polynomial, samplePoly



def derivative(P):

    c = P.coeffs()
    n = []
    for i in range(1, len(c)):
        n += [c[i] * i]

    return Polynomial(n)


def compute_residues(u, Q):

    K = Q.shape[0]
    J = Q.shape[1] - 1

    # DP solution
    U = np.zeros((K, J + 1), dtype=GF)

    # Base Case
    U[0][J] = u

    # Fill in the rest of the matrix
    for j in range(J, 0, -1):
        for i in range(0, K, 2 ** j):

            t = 2 ** (j - 1)
            
            U[i][j - 1] = U[i][j] % Q[i][j - 1]
            U[i + t][j - 1] = U[i][j] % Q[i + t][j - 1]
    

    return [e[0].coeffs()[0] for e in U][:len(u.coeffs())]

def compute_Q(P):

    K = int(2 ** (math.ceil(math.log(len(P), 2))))
    J = int(math.log(K, 2))

    # DP solution
    Q = np.ones((K, J + 1), dtype=GF)

    # Base case
    for i in range(len(P)):
        Q[i][0] = P[i]

    # Fill rest of the matrix in total time K log^2(K)
    for j in range(1, J + 1):
        for i in range(0, K, 2 ** j):
            t = 2 ** (j - 1)
            Q[i][j] = Q[i][j - 1] * Q[i + t][j - 1]

    return Q


def preconditioned_crt(P, D, U, Q):


    K = Q.shape[0]
    J = Q.shape[1] - 1

    S = np.zeros((K, J + 1), dtype=GF)


    # Base Case
    for i in range(len(D)):
        S[i][0] = D[i] * U[i]


    # Fill in the rest of the matrix in time 2K
    for j in range(1, J + 1):
        for i in range(0, K, 2 ** j):

            t = 2 ** (j - 1)
            t1 = Q[i + t][j - 1] * S[i][j - 1]
            t2 = Q[i][j - 1] * S[i + t][j - 1]

            S[i][j] = t2 + t1


    return S[0][J]


def interpolate(X, LY):

    # Compute p_i terms
    P = [Polynomial([-x, GF(1)]) for x in X]

    # Compute q terms 
    Q = compute_Q(P)

    # Extract p
    p = Q[0][len(Q[0]) - 1]

    # Compute dp(x)/dx
    dp = derivative(p)

    # Compute derivative evaluations
    C = compute_residues(dp, Q)

    # Compute inverses of derivative
    D = [~c for c in C]

    # Compute Chinese Remainder Algorithm with provided D, Q
    S = []
    for Y in LY:
        s = preconditioned_crt(P, D, Y, Q)

        if not isinstance(s, Polynomial):
            s = Polynomial([s])
            
        
        S += [s]

    return S


if __name__ == '__main__':

    # Sanity check
    
    X = [GF(1), GF(2), GF(3), GF(4)]
    Y = [GF(2), GF(7), GF(4), GF(8)]

    s = interpolate(X, [Y])[0]
    s2 = Polynomial([GF(-26), GF(89)/GF(2), GF(-19), GF(5)/GF(2)])

    assert s == s2

    # Evaluation Check

    d = 10
    P = samplePoly(d)
    X = [GF(x) for x in range(d)]

    pX = [Polynomial([-x, GF(1)]) for x in X]
    Q = compute_Q(pX)

    assert P(X) == compute_residues(P, Q)

    # Check interpolation.

    r = sampleGF()
    assert P(r) == interpolate(X, [P(X)])[0](r)
    

    
