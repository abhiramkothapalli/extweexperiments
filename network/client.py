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

        future_results_share = [n.handle_share_response.future(wrap((sr, zu))) for n in self.old_nodes]
        future_results_statement = [n.set_statement.future(wrap(statement)) for n in self.new_nodes]

        results_share = [r.result() for r in future_results_share]
        results_statement = [r.result() for r in future_results_statement]

        


    def reconstruct(self, statement, witness):

        # witness is the discrete log of challenge


        proof = schnorr.prove(statement, witness)

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
        


        

    
