#!/usr/bin/env python

import sys
sys.path.append('../src/')

import Pyro4
import dpss
from wrapper import Wrapper
import time
import vss

from threading import Lock

sys.excepthook = Pyro4.util.excepthook


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Node(Wrapper):

    def distribute(func):

        ''' Cached Distribution Decorator '''

        def wrapper(*args, **kwargs):


            key = func.__name__

            if key not in args[0].locks:
                args[0].locks[key] = Lock()

            args[0].locks[key].acquire()

            # If function is called for the first time compute
            # and cache the result
            if key not in args[0].cached:
                res = func(*args, **kwargs)
                args[0].cached[key] = res

            # Otherwise if node is calling for the first time
            # Pop element in the list and provide to node
            node = Pyro4.current_context.client.sock.getpeername()
            if node not in args[0].distributed:
                res = args[0].cached[key][int(args[1][0])][int(args[1][1])]
                args[0].distributed[node] = res

            args[0].locks[key].release()
                
            
            return args[0].distributed[node]

    
            
        return wrapper


    def cache(func):
        ''' Caching decorator '''

        def wrapper(*args, **kwargs):
            key = func.__name__

            if key not in args[0].locks:
                args[0].locks[key] = Lock()

            args[0].locks[key].acquire()
            
            if key not in args[0].cached:
                res = func(*args, **kwargs)
                args[0].cached[key] = res

            args[0].locks[key].release()


                
            return args[0].cached[key]
            
        return wrapper



    def __init__(self, u):

        self.u = u
        self.blacklist = []

        # Secret Share
        self.share = None
        self.com = None

        # Setup Randomness
        self.setup_shares = []
        self.setup_coms = []

        # Refresh Randomness and Commitments
        self.refresh_shares = []
        self.old_refresh_coms = []
        self.new_refresh_coms = []

        self.cached = {}
        self.distributed = {}
        self.locks = {}

    def set_params(self, params):

        n, pk = self.unwrap(params)
        
        self.n = n
        self.pk = pk

    def flush(self):

        self.blacklist = []

        # Secret Share
        self.share = None
        self.com = None

        # Setup Randomness
        self.setup_shares = []
        self.setup_coms = []

        # Refresh Randomness and Commitments
        self.refresh_shares = []
        self.old_refresh_coms = []
        self.new_refresh_coms = []

        self.cached = {}
        self.distributed = {}
        self.locks = {}


    ''' Create Randomness Key '''

    @distribute
    def setup_distribution(self, u):
        
        ss, C = dpss.setup_dist(self.pk)
        gss, gC = dpss.setup_dist(self.pk)

        shares = [self.wrap((ss[i], C, gss[i], gC)) for i in range(self.n)]

        return [shares]


    @cache
    def setup_distribution_verification(self):

        c = 10 # TODO: test this correctly

        nodes = self.get_old_nodes()

        future_results = [n.setup_distribution(u) for n in nodes]
        
        ss = []
        coms = []
        gss = []
        gcoms = []

        for res in future_results:
            s, C, gs, gC = self.unwrap(res.value)
            ss += [s]
            coms += [C]
            gss += [gs]
            gcoms += [gC]

        ns, ncom = dpss.setup_verification_dist(ss, coms, gss, gcoms, c)


        self.ss = ss
        self.coms = coms
        self.ncom = ncom

        return self.wrap(ns)


    def generate_setup_randomness(self):

        nodes = self.get_old_nodes()
        
        future_nss = [n.setup_distribution_verification() for n in nodes]
        nss = [self.unwrap(fnss.value) for fnss in future_nss]

        
        ncom = self.ncom

        assert dpss.setup_verification_check(self.pk, nss, ncom)

        rs, rcoms = dpss.setup_output(self.pk, self.ss, self.coms)

        self.setup_shares += rs
        self.setup_coms += rcoms



    ''' Create Refresh Randomness Key '''

    @distribute
    def distribution(self, u):

        ssC, sstCt = dpss.distribution(self.pk)
        gssC, gsstCt = dpss.distribution(self.pk)

        ss, C = ssC
        gss, gC = gssC
        sst, Ct = sstCt
        gsst, gCt = gsstCt

        old_msgs = [self.wrap((ss[i], C, Ct, gss[i], gC, gCt)) for i in range(self.n)]
        new_msgs = [self.wrap((sst[i], Ct, C, gsst[i], gCt, gC)) for i in range(self.n)]

        return [old_msgs, new_msgs]

    @cache
    def distribution_verification_1(self):

        nodes = self.get_new_nodes()

        future_msgs = [n.distribution(self.u) for n in nodes]


        ss = []
        Cs = []
        Cso = []
        gss = []
        gCs = []
        gCso = []

        for msg in future_msgs:
            s, C, Co, gs, gC, gCo = self.unwrap(msg.value)
            ss += [s]
            Cs += [C]
            Cso += [Co]
            gss += [gs]
            gCs += [gC]
            gCso += [gCo]


        # TODO test this correctly
        c = 10

        if self.u[0] == 0:
            ns, ncom, ncomt = dpss.verification_dist(ss, Cs, gss, gCs, Cso, gCso, c)
        else:
            ns, ncomt, ncom = dpss.verification_dist(ss, Cs, gss, gCs, Cso, gCso, c)


        self.ncom = ncom
        self.ncomt = ncomt

        self.ss = ss
        self.Cs = Cs
        self.Cso = Cso

        return self.wrap(ns)

    def distribution_verification_2(self):


        nodes = self.get_old_nodes()

        new_nodes = self.get_new_nodes()

        future_onss = [n.distribution_verification_1() for n in nodes]
        future_nnss = [n.distribution_verification_1() for n in new_nodes]

        onss = [self.unwrap(s.value) for s in future_onss]
        nnss = [self.unwrap(s.value) for s in future_nnss]

        ncom = self.ncom
        ncomt = self.ncomt


        return dpss.verification_check(self.pk, onss, ncom, nnss, ncomt)

    def generate_refresh_randomness(self):

        assert self.distribution_verification_2()

        rs, rcoms, rcomst = dpss.output(self.pk, self.ss, self.Cs, self.Cso)


        self.refresh_shares += rs
        self.old_refresh_coms += rcoms
        self.new_refresh_coms += rcomst


    ''' Share '''

    def handle_share_request(self):

        # Pick out a setup randomness key
        rs = self.setup_shares.pop(0)
        com = self.setup_coms.pop(0)

        self.rs = rs
        self.com = com # TODO: This might be the one we want

        return self.wrap((rs, com))


    def handle_share_response(self, srzu):

        s, r = self.unwrap(srzu)
        share, com = dpss.setup_fresh_parties(self.pk, s, r, self.rs, self.com)


        self.share = share
        self.com = com


    ''' Refresh '''


    def get_king(self):
        # TODO: Do not hardcode
        return self.get_node((0, 0))

    @cache
    def release_share(self):
        
        # Refresh Randomness
        rs = self.refresh_shares.pop(0)

        rcom = self.old_refresh_coms.pop(0)

        self.rcom = rcom # TODO: this is only for the king

        share, com = dpss.refresh_preprocessing(self.share, self.com, rs, rcom)

        return self.wrap(share)



    @cache
    def refresh_reconstruct(self):

        nodes = self.get_old_nodes()

        future_shares = [n.release_share() for n in nodes]
        shares = [self.unwrap(s.value) for s in future_shares]


        kcom = self.com + self.rcom
        kpi = dpss.refresh_king(self.pk, shares, kcom)

        return self.wrap((kpi, kcom))


        
    def refresh(self):


        # Get material from king
        king = self.get_king()
        ks, kcom = self.unwrap(king.refresh_reconstruct())

        # Retrieve refresh randomness from storage.

        rs = self.refresh_shares.pop(0) 
        rcom = self.new_refresh_coms.pop(0)

        new_share, new_com = dpss.refresh_postprocessing(self.pk, ks, kcom, rs, rcom)


        # Store new secret
        self.share = new_share
        self.com = new_com



    ''' Reconstruct '''


    def get_share(self):
        # TODO this should only be visible to client
        return self.wrap((self.share, self.com))

        
if __name__ == '__main__':


    i = sys.argv[1]
    j = sys.argv[2]
    NSHOST = sys.argv[3] #'127.0.0.1' #'192.168.1.1'
    NSPORT = int(sys.argv[4])
    
    u = (int(i), int(j))
    v = 2 * int(i) + int(j)

    # Create Node Object
    node = Node(u)

    # Register to Nameserver
    #daemon = Pyro4.Daemon('node' + str(v))
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS(host=NSHOST, port=NSPORT) 
    uri = daemon.register(node)
    ns.register(str(i) + str(j), uri)

    print('Starting Node: ' + str(u))

    daemon.requestLoop()

    



        

    

        

        

        

        

        
        
        
        

    

    
    


                
        
            
            
    

        





