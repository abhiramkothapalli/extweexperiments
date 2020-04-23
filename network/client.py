#!/usr/bin/env python

import dpss
from wrapper import Wrapper
import vss



class Client(Wrapper):

    def __init__(self, u, n, pk):

        self.pk = pk
        super().__init__(u, n)


    def listread(self, num, i):

        L = []
        for t in range(num):
            l = []
            for j in range(self.n):
                l += [self.read((i, j))]
            L += [l]

        return L



    def share(self, secret):


        nodes = self.get_old_nodes()

        future_shares = [n.handle_share_request() for n in nodes]


        rss = []
        coms = []
        for share in future_shares:
            rs, com = self.unwrap(share.value)
            rss += [rs]
            coms +=[com]

        com = coms[0] # TODO: do this better
        pk = self.pk
        sr, zu = dpss.share(pk, (rss, com), secret)

        for node in nodes:
            node.handle_share_response(self.wrap((sr, zu)))


    def reconstruct(self):

        nodes = self.get_new_nodes()

        future_shares = [node.get_share() for node in nodes]

        # TODO can reconstruct after t nodes
        ss = []
        coms = []
        for share in future_shares:
            s, com = self.unwrap(share.value)
            ss += [s]
            coms += [com]

        com = coms[0] # TODO: Find a better way

        s = dpss.reconstruct(self.pk, (ss, com))

        return s
        


        

    
