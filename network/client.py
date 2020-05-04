#!/usr/bin/env python

import Pyro4
import dpss
from wrapper import Wrapper
from serializer import wrap, unwrap
from concurrent import futures



class Client(Wrapper):


    def share(self, secret):

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
            n.handle_share_response(wrap((sr, zu)))
        


    def reconstruct(self):

        shares = [n.get_share.future(wrap(None)) for n in self.new_nodes]
        ss = []
        coms = []
        for share in shares:
            s, com = unwrap(share.result())
            ss += [s]
            coms += [com]

        com = coms[0] # TODO: Find a better way

        secret = dpss.reconstruct(self.pk, (ss, com))

        return secret
        


        

    
