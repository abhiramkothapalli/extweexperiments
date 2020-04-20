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

            # If function is called for the first time compute
            # and cache the result
            if key not in args[0].cached:
                res = func(*args, **kwargs)
                #args[0].lock.acquire()
                args[0].cached[key] = res
                #args[0].lock.release()


            # Otherwise if node is calling for the first time
            # Pop element in the list and provide to node
            node = Pyro4.current_context.client.sock.getpeername()
            if node not in args[0].distributed:
                #args[0].lock.acquire()
                res = args[0].cached[key].pop(0)
                #args[0].lock.release()
                
                args[0].distributed[node] = res
                
            
            return args[0].distributed[node]

    
            
        return wrapper


    def cache(func):
        ''' Caching decorator '''

        def wrapper(*args, **kwargs):
            key = func.__name__

            if key not in args[0].cached:
                #args[0].lock.acquire()
                res = func(*args, **kwargs)
                args[0].cached[key] = res
                #args[0].lock.release()


                
            return args[0].cached[key]
            
        return wrapper


    def get_old_nodes(self):
        return [self.get_node((0, j)) for j in range(self.n)]

    def get_new_nodes(self):
        return [self.get_node((1, j)) for j in range(self.n)]

    def __init__(self, u):

        self.u = u

        self.blacklist = []
        self.lock = Lock()

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

        super().flush()

    # TODO: Remove these methods
    def listread(self, num, i):

        L = []
        for t in range(num):
            l = []
            for j in range(self.n):
                if (i, j) in self.blacklist:
                    continue
                l += [self.read((i, j))]
            L += [l]

        return L

    def dispense(self, M, i):
        for j in range(self.n):
            self.send((i, j), M[j])



    ''' Create Randomness Key '''

    @distribute
    def setup_distribution(self):
        
        ss, C = dpss.setup_dist(self.pk)
        gss, gC = dpss.setup_dist(self.pk)

        shares = [self.wrap((ss[i], C, gss[i], gC))  for i in range(self.n)]


        return shares


    @cache
    def setup_distribution_verification(self):

        c = 10 # TODO: test this correctly

        nodes = self.get_old_nodes()
        
        ss = []
        coms = []
        gss = []
        gcoms = []

        for node in nodes:
            s, C, gs, gC = self.unwrap(node.setup_distribution())
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
        nss = [self.unwrap(node.setup_distribution_verification()) for node in nodes]
        ncom = self.ncom

        assert dpss.setup_verification_check(self.pk, nss, ncom)

        rs, rcoms = dpss.setup_output(self.pk, self.ss, self.coms)

        self.setup_shares += rs
        self.setup_coms += rcoms



    ''' Create Refresh Randomness Key '''


    def distribution(self):

        ssC, sstCt = dpss.distribution(self.pk)
        gssC, gsstCt = dpss.distribution(self.pk)

        ss, C = ssC
        gss, gC = gssC
        sst, Ct = sstCt
        gsst, gCt = gsstCt

        old_msgs = [(ss[i], C, Ct, gss[i], gC, gCt) for i in range(self.n)]
        new_msgs = [(sst[i], Ct, C, gsst[i], gCt, gC) for i in range(self.n)]

        self.dispense(old_msgs, 0)
        self.dispense(new_msgs, 1)

    def old_distribution_verification_1(self):

        L = self.listread(1, 1)[0] # Read from new parties

        ss = [l[0] for l in L]
        Cs = [l[1] for l in L]
        Cts = [l[2] for l in L]
        gss = [l[3] for l in L]
        gCs = [l[4] for l in L]
        gCts = [l[5] for l in L]


        # TODO test this correctly
        c = 10

        ns, ncom, ncomt = dpss.verification_dist(ss, Cs, gss, gCs, Cts, gCts, c)

        self.broadcast(ns, 0) # to Old parties
        self.broadcast(ns, 1) # to New parties
        self.ncom = ncom
        self.ncomt = ncomt

        self.ss = ss
        self.Cs = Cs
        self.Cts = Cts


    def new_distribution_verification_1(self):

        # TODO this is the same as above

        L = self.listread(1, 1)[0] # read from the new parties

        sst = [l[0] for l in L]
        Cts = [l[1] for l in L]
        Cs = [l[2] for l in L]
        gsst = [l[3] for l in L]
        gCts = [l[4] for l in L]
        gCs = [l[5] for l in L]



        # TODO test this correctly
        c = 10

        ns, ncomt, ncom = dpss.verification_dist(sst, Cts, gsst, gCts, Cs, gCs, c)

        self.broadcast(ns, 0) # To Old Parties
        self.broadcast(ns, 1) # To New parties
        self.ncom = ncom
        self.ncomt = ncomt


        self.sst = sst
        self.Cts = Cts
        self.Cs = Cs

    def distribution_verification_2(self):

        onss = self.listread(1, 0)[0]
        nnss = self.listread(1, 1)[0]

        ncom = self.ncom
        ncomt = self.ncomt



        assert dpss.verification_check(self.pk, onss, ncom, nnss, ncomt)



    def old_output(self):

        ss = self.ss
        Cs = self.Cs
        Cts = self.Cts

        rs, rcoms, rcomst = dpss.output(self.pk, ss, Cs, Cts)



        self.refresh_shares += rs
        self.old_refresh_coms += rcoms
        self.new_refresh_coms += rcomst

    def new_output(self):

        # TODO this is the same as above

        sst = self.sst
        Cts = self.Cts
        Cs = self.Cs

        rs, rcomst, rcoms = dpss.output(self.pk, sst, Cts, Cs)


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


    #@Pyro4.oneway
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

        for n in nodes:
            n._pyroAsync()

        future_shares = [n.release_share() for n in nodes]
        shares = [self.unwrap(s.value) for s in future_shares]


        kcom = self.com + self.rcom
        kpi = dpss.refresh_king(self.pk, shares, kcom)

        return self.wrap((kpi, kcom))


        
    #@Pyro4.oneway
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

    # Create Node Object
    node = Node(u)

    # Register to Nameserver
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS(host=NSHOST, port=NSPORT) 
    uri = daemon.register(node)
    ns.register(str(i) + str(j), uri)

    print('Starting Node: ' + str(u))

    daemon.requestLoop()

    



        

    

        

        

        

        

        
        
        
        

    

    
    


                
        
            
            
    

        





