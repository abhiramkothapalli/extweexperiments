#!/usr/bin/env python

import dpss
from wrapper import Wrapper
from serializer import wrap, unwrap
from concurrent import futures

import sys
sys.path.append('../src/')

import schnorr



class Client(Wrapper):


    def share(self, statement, secret):

        # Secret is released when someone finds discrete log of statement
        

        shares = [n.handle_share_request.future(wrap(None)) for n in self.old_nodes]
        rss = []
        coms = []
        for share in shares:
            rs, com = unwrap(share.result())
            rss += [rs]
            coms +=[com]


        com = coms[0] # TODO: Find a better way
        sr, zu = dpss.share(self.pk, (rss, com), secret)

        for n in self.old_nodes:
            n.handle_share_response(wrap((statement, (sr, zu))))
        


    def reconstruct(self, statement, witness):

        # witness is the discrete log of challenge


        proof = schnorr.prove(statement, witness)

        print('Client statement: ' + str(statement))
        print('Client proof: ' + str(proof[0]) + ', ' + str(proof[1]))

        # TODO: Client statement, proof verifies
        # But node does not
        print('Client side schnorr verification: ' + str(schnorr.verify(statement, proof)))

        shares = [n.get_share.future(wrap(proof)) for n in self.new_nodes]
        ss = []
        coms = []
        for share in shares:
            # ERROR HERE due to share result being none
            s, com = unwrap(share.result())
            ss += [s]
            coms += [com]

        com = coms[0] # TODO: Find a better way

        secret = dpss.reconstruct(self.pk, (ss, com))

        return secret
        


        

    
