#!/usr/bin/env python

import dpss
from wrapper import Wrapper
from serializer import wrap, unwrap
from concurrent import futures

import sys
sys.path.append('../src/')


class Client(Wrapper):


    def share(self, secret, i):

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

        future_results_share = [n.handle_share_response.future(wrap(((sr, zu), i))) for n in self.old_nodes]
        #future_results_application = [n.set_application.future(wrap(application)) for n in self.new_nodes]

        results_share = [r.result() for r in future_results_share]
        #results_application = [r.result() for r in future_results_application]




    def update(self, application, state, w, i):
        pi = application.request_update(w)
        future_results = [node.update_application_state.future(wrap((state, pi, i))) for node in self.new_nodes]
        [r.result() for r in future_results]


    def reconstruct(self, application, w, i):

        # witness is the discrete log of challenge


        pi = application.request_release(w)

        lshares = [n.get_share.future(wrap((pi, i))) for n in self.new_nodes]

        lshares = [unwrap(lshare.result()) for lshare in lshares]

        secrets = []
        for i in range(len(lshares[0])):


            shares = [lshare[i] for lshare in lshares]
        
            ss = []
            coms = []
            for share in shares:

                s, com = share
                ss += [s]
                coms += [com]

            if not coms or not ss:
                raise Exception('No shares returned. Client likely has invalid witness')

            com = coms[0] # TODO: Find a better way

            secret = dpss.reconstruct(self.pk, (ss, com))

            
            secrets += [secret]


        return secrets
        


        

    
