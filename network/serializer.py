import sys
sys.path.append('../src/')

import pickle # TODO: Use a more secure serializer

import grpc

# Import the generated classes
import services_pb2       # Messages
import services_pb2_grpc  # Services

def wrap(m):
        c = pickle.dumps(m, protocol=0)
        return services_pb2.Pickle(s=c)

def unwrap(c):
    m = pickle.loads(c.s)
    return m

# import Pyro4
# from Pyro4.util import SerializerBase
# from gfec import GF, EC1, EC2
# from vss import Proof

# Pyro4.config.SERIALIZER = "serpent"

# def gf_class_to_dict(e):
#     return {
#         '__class__' : 'GF',
#         'state' : e.__getstate__()
#     }

# def dict_to_gf_class(classname, d):
#     e = GF()
#     e.__setstate__(d['state'])
#     return e

# def ec1_class_to_dict(e):
#     return {
#         '__class__' : 'EC1',
#         'state' : e.__getstate__()
#     }

# def dict_to_ec1_class(classname, d):
#     e = EC1(None)
#     e.__setstate__(d['state'])
#     return e

# def ec2_class_to_dict(e):
#     return {
#         '__class__' : 'EC2',
#         'state' : e.__getstate__()
#     }

# def dict_to_ec2_class(classname, d):
#     e = EC2(None)
#     e.__setstate__(d['state'])
#     return e

# def proof_class_to_dict(e):
#     return {
#         '__class__' : 'Proof',
#         'state' : e.__getstate__()
#     }

# def dict_to_proof_class(classname, d):
#     e = Proof((None, None, None, None))
#     e.__setstate__(d['state'])
#     return e
    



# SerializerBase.register_class_to_dict(GF, gf_class_to_dict)
# SerializerBase.register_dict_to_class('GF', dict_to_gf_class)
# SerializerBase.register_class_to_dict(EC1, ec1_class_to_dict)
# SerializerBase.register_dict_to_class('EC1', dict_to_ec1_class)
# SerializerBase.register_class_to_dict(EC2, ec2_class_to_dict)
# SerializerBase.register_dict_to_class('EC2', dict_to_ec2_class)
# SerializerBase.register_class_to_dict(Proof, proof_class_to_dict)
# SerializerBase.register_dict_to_class('Proof', dict_to_proof_class)

