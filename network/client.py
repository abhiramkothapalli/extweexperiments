#!/usr/bin/env python

import Pyro4
import dpss
from wrapper import Wrapper


@Pyro4.behavior(instance_mode='single')
class Client(Wrapper):

    @Pyro4.expose
    def share(self, secret):

        shares = [n.handle_share_request() for n in self.old_nodes]
        rss = []
        coms = []
        for share in shares:
            rs, com = share.value
            rss += [rs]
            coms +=[com]

        com = coms[0] # TODO: Find a better way
        sr, zu = dpss.share(self.pk, (rss, com), secret)

        for n in self.old_nodes:
            n.handle_share_response((sr, zu))

    @Pyro4.expose
    def reconstruct(self):

        shares = [n.get_share() for n in self.new_nodes]
        ss = []
        coms = []
        for share in shares:
            s, com = share.value
            ss += [s]
            coms += [com]

        com = coms[0] # TODO: Find a better way

        secret = dpss.reconstruct(self.pk, (ss, com))

        return secret
        


        

    
