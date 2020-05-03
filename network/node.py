#!/usr/bin/env python

import sys
sys.path.append('../src/')

import Pyro4
import dpss
from wrapper import Wrapper
import time
import vss
import params

from threading import Lock

sys.excepthook = Pyro4.util.excepthook

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

@Pyro4.behavior(instance_mode="single")
class Node(Wrapper):

    def __init__(self, u, NSHOST, NSPORT):

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

        super().__init__(u, NSHOST, NSPORT)


    @Pyro4.expose
    def flush(self):

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

        
    def get_challenge(self):
        # CONFIGURE: In practice this is sampled from a trusted bulletin board
        # such as the blockchain.
        return 10


    ''' Create Randomness Key '''

    @Pyro4.expose
    @distribute
    def setup_distribution(self, u):

        ss, C = dpss.setup_dist(self.pk)
        gss, gC = dpss.setup_dist(self.pk)

        shares = [(ss[i], C, gss[i], gC) for i in range(self.n)]

        return [shares]


    @Pyro4.expose
    @cache
    def setup_distribution_verification(self):

        c = self.get_challenge()

        nodes = self.old_nodes

        request_results = [n.setup_distribution(u) for n in nodes]
        
        ss = []
        coms = []
        gss = []
        gcoms = []

        for res in request_results:
            s, C, gs, gC = res.value
            ss += [s]
            coms += [C]
            gss += [gs]
            gcoms += [gC]

        ns, ncom = dpss.setup_verification_dist(ss, coms, gss, gcoms, c)

        self.ss = ss
        self.coms = coms
        self.ncom = ncom

        return ns


    @Pyro4.expose
    def generate_setup_randomness(self):

        
        request_nss = [n.setup_distribution_verification() for n in self.old_nodes]
        nss = [fnss.value for fnss in request_nss]
        ncom = self.ncom

        assert dpss.setup_verification_check(self.pk, nss, ncom)

        rs, rcoms = dpss.setup_output(self.pk, self.ss, self.coms)

        self.setup_shares += rs
        self.setup_coms += rcoms



    ''' Create Refresh Randomness Key '''

    @Pyro4.expose
    @distribute
    def distribution(self, u):

        ssC, sstCt = dpss.distribution(self.pk)
        gssC, gsstCt = dpss.distribution(self.pk)

        ss, C = ssC
        gss, gC = gssC
        sst, Ct = sstCt
        gsst, gCt = gsstCt

        old_msgs = [(ss[i], C, Ct, gss[i], gC, gCt) for i in range(self.n)]
        new_msgs = [(sst[i], Ct, C, gsst[i], gCt, gC) for i in range(self.n)]

        return [old_msgs, new_msgs]

    @Pyro4.expose
    @cache
    def distribution_verification_1(self):

        request_msgs = [n.distribution(self.u) for n in self.new_nodes]

        ss = []
        Cs = []
        Cso = []
        gss = []
        gCs = []
        gCso = []

        for msg in request_msgs:
            s, C, Co, gs, gC, gCo = msg.value
            ss += [s]
            Cs += [C]
            Cso += [Co]
            gss += [gs]
            gCs += [gC]
            gCso += [gCo]


        c = self.get_challenge()

        if self.u[0] == 0:
            ns, ncom, ncomt = dpss.verification_dist(ss, Cs, gss, gCs, Cso, gCso, c)
        else:
            ns, ncomt, ncom = dpss.verification_dist(ss, Cs, gss, gCs, Cso, gCso, c)


        self.ncom = ncom
        self.ncomt = ncomt

        self.ss = ss
        self.Cs = Cs
        self.Cso = Cso

        return ns

    def distribution_verification_2(self):

        request_onss = [n.distribution_verification_1() for n in self.old_nodes]
        request_nnss = [n.distribution_verification_1() for n in self.new_nodes]

        onss = [s.value for s in request_onss]
        nnss = [s.value for s in request_nnss]

        ncom = self.ncom
        ncomt = self.ncomt

        return dpss.verification_check(self.pk, onss, ncom, nnss, ncomt)

    @Pyro4.expose
    def generate_refresh_randomness(self):

        assert self.distribution_verification_2()

        rs, rcoms, rcomst = dpss.output(self.pk, self.ss, self.Cs, self.Cso)

        self.refresh_shares += rs
        self.old_refresh_coms += rcoms
        self.new_refresh_coms += rcomst


    ''' Share '''

    @Pyro4.expose
    def handle_share_request(self):

        # If no setup randomness available
        # then generate more.
        if not self.setup_shares:
            self.generate_setup_randomness()

        # Pick out a setup randomness key
        rs = self.setup_shares.pop(0)
        com = self.setup_coms.pop(0)

        self.rs = rs
        self.com = com

        return (rs, com)


    @Pyro4.expose
    def handle_share_response(self, srzu):

        s, r = srzu
        share, com = dpss.setup_fresh_parties(self.pk, s, r, self.rs, self.com)

        self.share = share
        self.com = com


    ''' Refresh '''


    def get_king(self):
        # CONFIGURE: In practice, the king will change each round.
        return self.old_nodes[0]


    @Pyro4.expose
    @cache
    def release_share(self):

        # Refresh Randomness
        rs = self.refresh_shares.pop(0)
        rcom = self.old_refresh_coms.pop(0)
        self.rcom = rcom

        share, com = dpss.refresh_preprocessing(self.share, self.com, rs, rcom)

        return share



    @Pyro4.expose
    @cache
    def refresh_reconstruct(self):

        request_shares = [n.release_share() for n in self.old_nodes]
        shares = [s.value for s in request_shares]

        kcom = self.com + self.rcom
        kpi = dpss.refresh_king(self.pk, shares, kcom)

        return (kpi, kcom)


    @Pyro4.expose
    def refresh(self):

        king = self.get_king()

        # If no setup randomness available
        # then generate more.
        if not self.refresh_shares:
            self.generate_refresh_shares()

        # Get material from king
        king = self.get_king()
        ks, kcom = king.refresh_reconstruct().value

        # Retrieve refresh randomness from storage.

        rs = self.refresh_shares.pop(0) 
        rcom = self.new_refresh_coms.pop(0)

        new_share, new_com = dpss.refresh_postprocessing(self.pk, ks, kcom, rs, rcom)

        # Store new secret
        self.share = new_share
        self.com = new_com


    @Pyro4.expose
    @cache
    def dummy_release_share(self):
        return 'done'

    @Pyro4.expose
    @cache
    def dummy_refresh_reconstruct(self):
        request_shares = [n.release_share() for n in self.old_nodes]
        shares = [s.value for s in request_shares]
        return 'done'

    @Pyro4.expose
    def dummy_refresh(self):
        # Get material from king
        king = self.get_king()
        result = king.dummy_refresh_reconstruct().value
        return result

    @Pyro4.expose
    def ping(self, data):
        return 'pong'



    ''' Reconstruct '''


    @Pyro4.expose
    def get_share(self):
        # CONFIGURE this should only be visible to client

        if not self.share:
            raise Exception('Node ' + str(self.u) + ' does not have requested share')
        else:
            return (self.share, self.com)

        
if __name__ == '__main__':

    Pyro4.config.THREADPOOL_SIZE = params.THREADPOOL_SIZE

    i = sys.argv[1]
    j = sys.argv[2]
    NODEHOST = sys.argv[3]
    NSHOST = sys.argv[4]
    NSPORT = int(sys.argv[5])
    
    u = (int(i), int(j))
    v = 2 * int(i) + int(j)

    # Create Node Object
    node = Node(u, NSHOST, NSPORT)

    # Register to Nameserver
    daemon = Pyro4.Daemon(NODEHOST)

    print('Node ' + str(u) + ': Attempting to connect to name server')

    while True:
        try:
            ns = Pyro4.locateNS(host=NSHOST, port=NSPORT)
            break
        except:
            time.sleep(10)
    
    uri = daemon.register(node)
    ns.register(str(i) + str(j), uri)

    print('Node ' + str(u) + ': Starting')

    daemon.requestLoop()

    



        

    

        

        

        

        

        
        
        
        

    

    
    


                
        
            
            
    

        





