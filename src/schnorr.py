from gfec import *
import hashlib


def fs_challenge(t):
    t.normalize()

    a = hashlib.sha256(str(t).encode())
    return GF(int(a.hexdigest(), 16))



def prove(statement, witness):

    r = sampleGF()
    t = g1 * r
    c = fs_challenge(t)
    s = r + c * witness

    return (t, s)

def verify(statement, proof):

    t, s = proof
    c = fs_challenge(t)

    return g1 * s == t + statement * c

if __name__ == '__main__':

    witness = sampleGF()
    incorrect_witness = sampleGF()
    
    statement = g1 * witness

    proof = prove(statement, witness)
    incorrect_proof = prove(statement, incorrect_witness)

    assert verify(statement, proof)
    assert not verify(statement, incorrect_proof)

    
