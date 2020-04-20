#!/usr/bin/env python

import random
from lib.atepairing.python.wrapper import *

# Setup must always be called upon loading library
setup()

order = int(get_order())

class GF(object):

    def __init__(self, n):
        if isinstance(n, str):
            self.n = str(int(n) % order)
        if isinstance(n, int):
            self.n = str(n % order) # Could add n % order

    def __add__(self, o):
        if isinstance(o, GF):
            return GF(add(self.n, o.n))
        elif isinstance(o, int):
            return GF(add(self.n, GF(o).n))
        else:
            raise NotImplementedError

    __radd__ = __add__

    def __sub__(self, o):
        if isinstance(o, GF):
            return GF(sub(self.n, o.n))
        elif isinstance(o, int):
            return GF(sub(self.n, GF(o).n))
        else:
            raise NotImplementedError

    def __mul__(self, o):
        if isinstance(o, GF):
            return GF(mul(self.n, o.n))
        elif isinstance(o, int):
            return GF(mul(self.n, GF(o).n))
        else:
            raise NotImplementedError

    __rmul__ = __mul__

    def __truediv__(self, o):
        if isinstance(o, GF):
            return GF(div(self.n, o.n))
        elif isinstance(o, int):
            return GF(div(self.n, GF(o).n))
        else:
            raise NotImplementedError

    def __neg__(self):
        return GF(neg(self.n))

    def __invert__(self):
        return GF(inv(self.n))

    def __eq__(self, o):
        return self.n == o.n

    def __repr__(self):
        return repr(self.n)

    def __str__(self):
        return str(self.n)

def sampleGF():
    return GF(str(random.randint(0, order)))



class EC1(object):

    def __init__(self, n):
        self.n = n

    def __mul__(self, o):
        if isinstance(o, GF):
            return EC1(ec1smul(self.n, o.n))
        elif isinstance(o, int):
            return EC1(ec1smul(self.n, GF(o).n))
        elif isinstance(o, EC2):
            return EC12(pairing(self.n, o.n))
        else:
            raise NotImplementedError

    __rmul__ = __mul__

    def __add__(self, o):
        if isinstance(o, EC1):
            return EC1(ec1add(self.n, o.n))
        else:
            raise NotImplementedError

    def __sub__(self, o):
        if isinstance(o, EC1):
            return EC1(ec1sub(self.n, o.n))
        else:
            raise NotImplementedError

    def __eq__(self, o):
        return ec1eq(self.n, o.n)

    def __str__(self):
        return str(self.n)
    
    def __repr__(self):
        return repr(self.n)


class EC2(object):

    def __init__(self, n):
        self.n = n

    def __mul__(self, o):
        if isinstance(o, GF):
            return EC2(ec2smul(self.n, o.n))
        elif isinstance(o, int):
            return EC2(ec2smul(self.n, GF(o).n))
        elif isinstance(o, EC1):
            return EC12(pairing(o.n, self.n))
        else:
            raise NotImplementedError

    __rmul__ = __mul__
        

    def __add__(self, o):
        if isinstance(o, EC2):
            return EC2(ec2add(self.n, o.n))
        else:
            raise NotImplementedError

    def __sub__(self, o):
        if isinstance(o, EC2):
            return EC2(ec2sub(self.n, o.n))
        else:
            raise NotImplementedError

    def __eq__(self, o):
        return ec2eq(self.n, o.n)

    def __str__(self):
        return str(self.n)
    
    def __repr__(self):
        return repr(self.n)


class EC12(object):

    # TODO add c++ wrapper for add, sub

    def __init__(self, n):
        self.n = n

    def __mul__(self, o):
        if isinstance(o, EC12):
            return EC12(ec12mul(self.n, o.n))
        else:
            raise NotImplementedError

    def __eq__(self, o):
        return self.n == o.n
        #return ec12eq(self.n, o.n) #TODO: Use proper definition

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return repr(self.n)
    


g1 = EC1(get_g1())
g2 = EC2(get_g2())

def pair(a, b):
    return EC12(pairing(a.n, b.n))



if __name__ == '__main__':



    '''Field'''

    # Sample field elements.
    a = sampleGF()
    b = sampleGF()
    c = sampleGF()
    d = sampleGF()

    x = 10
    y = 20
    z = 30


    # typing checks
    assert GF(x) + GF(y) == GF(x + y)
    assert GF(x) - GF(y) == GF(x - y)
    assert GF(x) * GF(y) == GF(x * y)

    # Neg check
    assert -GF(x) == GF(-x)

    # Add/Mult inverse test
    assert (a + (-a)) == GF(0)
    assert a * ~a == GF(1)

    # Check distributive property
    assert (d * (a + b - c)) == (d * a + d * b - d * c)


    '''Group'''


    # Order check
    assert g1 == g1 * (GF(order) + 1)

    # Scalar mult check
    assert g1 * 2 == g1 + g1
    assert g1 + g1 + g1 == g1 * 3


    # Check Associativity
    assert (g1 + g1) + g1 == g1 + (g1 + g1)

    # Check Commutativity
    g1x = g1 * x
    g1y = g1 * y
    assert g1x + g1y == g1y + g1x

    
    # Check Distributive Property
    assert g1 * x + g1 * y == g1 * (x + y)
    assert g1 * a + g1 * b == g1 * (a + b)


    # Basic homomorphic checks
    assert g1 * a + g1 * b + g1 * c + g1 * d == g1 * (a + b + c + d)
    assert g1 * a + g1 * a + g1 * a + g1 * a + g1 * a == g1 * (5 * a)



    # Twist Curve Checks
    assert g2 * (a + b) == g2 * a + g2 * b


    # Pairing checks
    p1 = pair(g1 * b, g2 * a)
    p2 = pair(g1 * (a * b), g2)
    p3 = pair(g1 * a + g1 * b, g2 * a - g2 * b)
    p4 = pair(g1, g2 * (a * a - b * b))
    assert p1 == p2
    assert p3 == p4
    assert p1 * p3 == p2 * p4
    
    







