#!/usr/bin/env python

import random
from lib.atepairing.python.gfeccore import *

# Setup must always be called upon loading library
setup()
order = int(get_order())

class GF(object):

    def __init__(self, n='0'):
        if isinstance(n, str):
            self.n = new_gf(str(int(n) % order))
        elif isinstance(n, int):
            self.n = new_gf(str(n % order))
        else:
            # Assume its a swig pointer
            # TODO this needs to be more robust
            self.n = n

    def __add__(self, o):
        if isinstance(o, GF):
            n = new_gf('0')
            add(n, self.n, o.n)
            return GF(n)
        elif isinstance(o, int):
            n = new_gf('0')
            add(n, self.n, GF(o).n)
            return GF(n)
        else:
            raise NotImplementedError

    __radd__ = __add__

    def __sub__(self, o):
        if isinstance(o, GF):
            n = new_gf('0')
            sub(n, self.n, o.n)
            return GF(n)
        elif isinstance(o, int):
            n = new_gf('0')
            sub(n, self.n, GF(o).n)
            return GF(n)
        else:
            raise NotImplementedError

    def __mul__(self, o):
        if isinstance(o, GF):
            n = new_gf('0')
            mul(n, self.n, o.n)
            return GF(n)
        elif isinstance(o, int):
            n = new_gf('0')
            mul(n, self.n, GF(o).n)
            return GF(n)
        else:
            raise NotImplementedError

    __rmul__ = __mul__

    def __truediv__(self, o):
        if isinstance(o, GF):
            n = new_gf('0')
            div(n, self.n, o.n)
            return GF(n)
        elif isinstance(o, int):
            n = new_gf('0')
            div(n, self.n, GF(o).n)
            return GF(n)
        else:
            raise NotImplementedError

    def __neg__(self):
        n = new_gf('0')
        neg(n, self.n)
        return GF(n)

    def __invert__(self):
        n = new_gf('0')
        inv(n, self.n)
        return GF(n)

    def __eq__(self, o):
        return eq(self.n, o.n)

    def __repr__(self):
        return repr(self.n)

    def __str__(self):
        return str(to_string(self.n))

    def __getstate__(self):
        return to_string(self.n)

    def __setstate__(self, s):
        n = new_gf(s)
        self.n = n
    
    # def __del__(self):
    #     try:
    #         remove(self.n)
    #     except:
    #         pass


def sampleGF():
    return GF(random.randint(0, order))

class EC(object):

    def __init__(self, n):
        self.n = n

    def __eq__(self, o):
        return eq(self.n, o.n)


    def __str__(self):
        return str(to_string(self.n))
    
    def __repr__(self):
        return repr(self.n)

    # def __del__(self):
    #     try:
    #         remove(self.n)
    #         pass
    #     except:
    #         pass


    

class EC1(EC):

    def __mul__(self, o):
        if isinstance(o, GF):
            e = new_ec1()
            smul(e, self.n, o.n)
            return EC1(e)
        elif isinstance(o, int):
            e = new_ec1()
            smul(e, self.n, GF(o).n)
            return EC1(e)
        elif isinstance(o, EC2):
            e = new_fp12()
            pairing(e, self.n, o.n)
            return EC12(e)
        else:
            raise NotImplementedError

    __rmul__ = __mul__

    def __add__(self, o):
        if isinstance(o, EC1):
            e = new_ec1()
            add(e, self.n, o.n)
            return EC1(e)
        else:
            raise NotImplementedError

    def __sub__(self, o):
        if isinstance(o, EC1):
            e = new_ec1()
            sub(e, self.n, o.n)
            return EC1(e)
        else:
            raise NotImplementedError


    def __getstate__(self):
        return to_string(self.n).split(',')

    def __setstate__(self, s):
        n = new_ec1(s[0], s[1], s[2])
        
        self.n = n



        

class EC2(EC):

    def __mul__(self, o):
        if isinstance(o, GF):
            e = new_ec2()
            smul(e, self.n, o.n)
            return EC2(e)
        elif isinstance(o, int):
            e = new_ec2()
            smul(e, self.n, GF(o).n)
            return EC2(e)
        elif isinstance(o, EC1):
            e = new_fp12()
            pairing(e, o.n, self.n)
            return EC12(e)
        else:
            raise NotImplementedError

    __rmul__ = __mul__
        

    def __add__(self, o):
        if isinstance(o, EC2):
            e = new_ec2()
            add(e, self.n, o.n)
            return EC2(e)
        else:
            raise NotImplementedError

    def __sub__(self, o):
        if isinstance(o, EC2):
            e = new_ec2()
            sub(e, self.n, o.n)
            return EC2(e)
        else:
            raise NotImplementedError

    def __getstate__(self):
        return to_string(self.n).split(',')

    def __setstate__(self, s):
        n = new_ec2(s[0], s[1], s[2], s[3], s[4], s[5])
        self.n = n


class EC12(EC):

    def __mul__(self, o):
        if isinstance(o, EC12):
            e = new_fp12()
            mul(e, self.n, o.n)
            return EC12(e)
        else:
            raise NotImplementedError
    
g1 = EC1(get_g1())
g2 = EC2(get_g2())

def pair(a, b):
    e = new_fp12()
    pairing(e, a.n, b.n)
    return EC12(e)

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

    # Printing tests
    print('g1: ' + str(g1))
    a = g1
    a_state = a.__getstate__()
    b = EC1(None)
    b.__setstate__(a_state)
    print(b)
    assert a == b


    print('g2: ' + str(g2))
    a = g2
    a_state = a.__getstate__()
    b = EC2(None)
    b.__setstate__(a_state)
    print(b)
    assert a == b
    #print(p1)


    
    







