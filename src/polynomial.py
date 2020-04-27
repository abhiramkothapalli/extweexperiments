#!/usr/bin/env/python

from gfec import GF, sampleGF
import numpy as np


class Polynomial():

    def __init__(self, p):

        # TODO: Consider stripping tailing zeros
        self.p = np.array(p)

    def __add__(self, o):
        if (isinstance(o, GF) or
            isinstance(o, int)):

            q = np.copy(self.p)
            q[0] += o

            return Polynomial(q)
        
        elif isinstance(o, Polynomial):

            m = min(self.p.size, o.p.size)
            if self.p.size > o.p.size:
                l = self.p[m:]
            else:
                l = o.p[m:]
            q = np.append(self.p[:m] + o.p[:m], l)
                
            return Polynomial(q)


    __radd__ = __add__

    def __sub__(self, o):
        if (isinstance(o, GF) or
            isinstance(o, int)):

            q = np.copy(self.p)
            q[0] -= o

            return Polynomial(q)
        
        elif isinstance(o, Polynomial):

            m = min(self.p.size, o.p.size)
            if self.p.size > o.p.size:
                l = self.p[m:]
            else:
                l = o.p[m:]
            q = np.append(self.p[:m] - o.p[:m], l)
                
            return Polynomial(q)

    def __mul__(self, o):

        if (isinstance(o, GF) or
            isinstance(o, int)):

            return Polynomial(self.p * o)

        elif isinstance(o, Polynomial):

            return Polynomial(np.convolve(self.p, o.p))

    __rmul__ = __mul__

    def _div(self, a, b):

        c1 = np.copy(a)
        c2 = np.copy(b)

        

        lc1 = len(c1)
        lc2 = len(c2)
        if lc1 < lc2:
            return c1[:1]*0, c1
        elif lc2 == 1:
            return c1/c2[-1], c1[:1]*0
        else:
            dlen = lc1 - lc2
            scl = c2[-1]
            c2 = c2[:-1]/scl
            i = dlen
            j = lc1 - 1
            while i >= 0:
                c1[i:j] -= c2*c1[j]
                i -= 1
                j -= 1
            return c1[j+1:]/scl, c1[:j+1]

    # TODO: consider adding remainder in final result
    def __truediv__(self, o):
        if (isinstance(o, GF) or
            isinstance(o, int)):

            quot, rem = self._div(self.p, [o])

            return Polynomial(quot)

        elif isinstance(o, Polynomial):

            quot, rem = self._div(self.p, o.p)

            return Polynomial(quot)#, Polynomial(rem)

        else:
            raise NotImplementedError

    def __mod__(self, o):

        if isinstance(o, Polynomial):

            quot, rem = self._div(self.p, o.p)

            return Polynomial(rem)

        elif (isinstance(o, GF) or
            isinstance(o, int)):

            quot, rem = self._div(self.p, [o])

            return Polynomial(rem)


    # TODO: potentially make this and code above do eval on lists
    def _eval(self, x):
        t = self.p[0]
        xp = x
        for i in range(1, len(self.p)):
            # TODO: can use compute_residues here
            t += self.p[i] * xp
            xp = xp * x
        return t
    
    def __call__(self, X):

        if isinstance(X, GF):
            return self._eval(X)
        elif isinstance(X, int):
            return self._eval(GF(X))

        Y = []
        for x in X:
            Y.append(self._eval(x))
        return Y

    def __eq__(self, o):
        return np.array_equal(self.p, o.p)


    def __str__(self):
        return str(self.p)

    def __repr__(self):
        return repr(self.p)

    def coeffs(self):
        return self.p.tolist()


def samplePoly(d, s=None):

    P = Polynomial([sampleGF() for i in range(0, d)])

    if s is not None:
        if isinstance(s, GF):
            P.p[0] = s
        elif isinstance(s, int):
            P.p[0] = GF(s)
        else:
            raise NotImplementedError

    return P


if __name__ == '__main__':

    dp = 10
    dq = 5

    O = samplePoly(dp)
    P = samplePoly(dp)
    Q = samplePoly(dq)

    # Manual sanity checks
    R = Polynomial([GF(-1), GF(1)])
    S = Polynomial([GF(1), GF(1)])
    T = Polynomial([GF(-1), GF(0), GF(1)])

    # Sample a point to evaluate.
    u = sampleGF()

    # Perform a low degree test.
    assert T(u) == (R * S)(u)

    # Check actual polynomial equality.
    assert T == R * S

    # Check division.
    assert T / R == S
    assert T / S == R
    assert (O + P) / Q == O / Q + P / Q

    
    # Degrees of random polynomials.
    dp = 10
    dq = 5

    # Sample two random polynomials.
    P = samplePoly(dp)
    Q = samplePoly(dq)

    # mul and div test
    assert P == (P * Q) / Q

    # add and sub test
    assert P == (P - Q) + Q

    # Scalar add/mul test
    assert P + P == 2 * P

    # Sample a set of points
    X = [sampleGF() for i in range(0, dp)]

    # Check polynomial secret point.
    R = samplePoly(dp, GF(15))
    assert R.coeffs()[0] == GF(15)
    assert R(GF(0)) == GF(15)





    


