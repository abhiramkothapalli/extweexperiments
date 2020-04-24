#!/usr/bin/env python

import dpss
from wrapper import Wrapper

class Client(Wrapper):

    def share(self, secret):

        nodes = self.old_nodes

        future_shares = [n.handle_share_request() for n in nodes]

        rss = []
        coms = []
        for share in future_shares:
            rs, com = self.unwrap(share.value)
            rss += [rs]
            coms +=[com]

        com = coms[0] # TODO: Find a better way
        pk = self.pk
        sr, zu = dpss.share(pk, (rss, com), secret)

        for node in nodes:
            node.handle_share_response(self.wrap((sr, zu)))


    def reconstruct(self):

        nodes = self.new_nodes

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
        


        

    
