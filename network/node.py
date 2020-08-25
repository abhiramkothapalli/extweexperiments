#!/usr/bin/env python
from concurrent import futures
import sys
sys.path.append('../src/')
from gfec import sampleGF

import grpc
import services_pb2       # Messages
import services_pb2_grpc  # Services

import dpss
import time
import vss
import params
import argparse
import logging
from wrapper import Wrapper

from serializer import wrap, unwrap

from threading import Lock

import schnorr



def distribute(func):

    ''' Cached Distribution Decorator '''

    def wrapper(*args, **kwargs):

        key = func.__name__

        if key not in args[0].locks:
            args[0].locks[key] = Lock()

        args[0].locks[key].acquire()
        try:

            # If function is called for the first time compute
            # and cache the result
            if key not in args[0].cached:
                res = func(*args, **kwargs)
                args[0].cached[key] = res


            nid = unwrap(args[1])

            j = nid % args[0].n
            i = 0
            if nid >= args[0].n:
                i = 1

            # Otherwise if node is calling for the first time
            # Pop element in the list and provide to node
            if nid not in args[0].distributed:
                res = args[0].cached[key][i][j]
                args[0].distributed[nid] = res

        except:
            args[0].locks[key].release()
        args[0].locks[key].release()

            
        return wrap(args[0].distributed[nid])
            
    return wrapper


def cache(func):

    ''' Caching decorator '''

    def wrapper(*args, **kwargs):
        key = func.__name__

        if key not in args[0].locks:
            args[0].locks[key] = Lock()

        args[0].locks[key].acquire()
        try:
            if key not in args[0].cached:
                res = func(*args, **kwargs)
                args[0].cached[key] = res
        except:
            args[0].locks[key].release()
        args[0].locks[key].release()
                
        return wrap(args[0].cached[key])
            
    return wrapper
    

class Node(Wrapper):

    def __init__(self, addr, nid, config):

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

        old_addrs = config[0]
        new_addrs = config[1]

        self.nid = int(nid)
        self.addr = addr

        super().__init__(old_addrs, new_addrs)

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

        return wrap(None)

        
    def get_challenge(self):
        # CONFIGURE: In practice this is sampled from a trusted bulletin board
        # such as the blockchain.
        return 10


    ''' Create Randomness Key '''

    @distribute
    def setup_distribution(self, request, context):

        ss, C = dpss.setup_dist(self.pk)
        gss, gC = dpss.setup_dist(self.pk)

        shares = [(ss[i], C, gss[i], gC) for i in range(self.n)]

        return [shares]

    @cache
    def setup_distribution_verification(self, request, context):

        c = self.get_challenge()

        request_results = [n.setup_distribution.future(wrap(self.nid)) for n in self.old_nodes]

        ss = []
        coms = []
        gss = []
        gcoms = []

        for r in request_results:
            s, C, gs, gC = unwrap(r.result())
            ss += [s]
            coms += [C]
            gss += [gs]
            gcoms += [gC]



        ns, ncom = dpss.setup_verification_dist(ss, coms, gss, gcoms, c)

        self.ss = ss
        self.coms = coms
        self.ncom = ncom

        return ns


    def generate_setup_randomness(self, request, context):


        request_nss = [n.setup_distribution_verification.future(wrap(None)) for n in self.old_nodes]
        nss = [unwrap(fnss.result()) for fnss in request_nss]
        ncom = self.ncom

        assert dpss.setup_verification_check(self.pk, nss, ncom)

        rs, rcoms = dpss.setup_output(self.pk, self.ss, self.coms)

        self.setup_shares += rs
        self.setup_coms += rcoms



        return wrap(None)



    ''' Create Refresh Randomness Key '''

    @distribute
    def distribution(self, request, context):

        ssC, sstCt = dpss.distribution(self.pk)
        gssC, gsstCt = dpss.distribution(self.pk)

        ss, C = ssC
        gss, gC = gssC
        sst, Ct = sstCt
        gsst, gCt = gsstCt

        old_msgs = [(ss[i], C, Ct, gss[i], gC, gCt) for i in range(self.n)]
        new_msgs = [(sst[i], Ct, C, gsst[i], gCt, gC) for i in range(self.n)]

        return [old_msgs, new_msgs]

    @cache
    def distribution_verification_1(self, result, context):


        request_msgs = [n.distribution.future(wrap(self.nid)) for n in self.new_nodes]

        ss = []
        Cs = []
        Cso = []
        gss = []
        gCs = []
        gCso = []

        for msg in request_msgs:
            s, C, Co, gs, gC, gCo = unwrap(msg.result())
            ss += [s]
            Cs += [C]
            Cso += [Co]
            gss += [gs]
            gCs += [gC]
            gCso += [gCo]


        c = self.get_challenge()

        if self.nid < self.n:
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

        request_onss = [n.distribution_verification_1.future(wrap(None)) for n in self.old_nodes]
        request_nnss = [n.distribution_verification_1.future(wrap(None)) for n in self.new_nodes]

        onss = [unwrap(s.result()) for s in request_onss]
        nnss = [unwrap(s.result()) for s in request_nnss]

        ncom = self.ncom
        ncomt = self.ncomt

        return dpss.verification_check(self.pk, onss, ncom, nnss, ncomt)

    def generate_refresh_randomness(self, request, context):

        assert self.distribution_verification_2()

        rs, rcoms, rcomst = dpss.output(self.pk, self.ss, self.Cs, self.Cso)

        self.refresh_shares += rs
        self.old_refresh_coms += rcoms
        self.new_refresh_coms += rcomst

        return wrap(None)


    ''' Share '''

    def handle_share_request(self, request, context):

        # If no setup randomness available
        # then generate more.
        if not self.setup_shares:
            self.generate_setup_randomness(None, None)

        # Pick out a setup randomness key
        rs = self.setup_shares.pop(0)
        com = self.setup_coms.pop(0)

        self.rs = rs
        self.com = com

        return wrap((rs, com))


    def handle_share_response(self, request, context):

        srzu = unwrap(request)
        s, r = srzu
        share, com = dpss.setup_fresh_parties(self.pk, s, r, self.rs, self.com)

        self.share = share
        self.com = com

        return wrap(None)

    # TODO This should be polled from a trusted party such as the bulletin board
    def set_application(self, request, context):
        self.application = unwrap(request)
        return wrap(None)

    ''' Refresh '''


    def get_king(self):
        # CONFIGURE: In practice, the king will change each round.
        return self.old_nodes[0]


    @cache
    def release_share(self, request, context):

        # Refresh Randomness
        rs = self.refresh_shares.pop(0)
        rcom = self.old_refresh_coms.pop(0)
        self.rcom = rcom

        share, com = dpss.refresh_preprocessing(self.share, self.com, rs, rcom)

        return share


    @cache
    def refresh_reconstruct(self, request, context):

        request_shares = [n.release_share.future(wrap(None)) for n in self.old_nodes]
        shares = [unwrap(s.result()) for s in request_shares]

        kcom = self.com + self.rcom
        kpi = dpss.refresh_king(self.pk, shares, kcom)

        return (kpi, kcom)


    def refresh(self, request, context):

        king = self.get_king()

        # If no setup randomness available
        # then generate more.
        if not self.refresh_shares:
            self.generate_refresh_shares()

        # Get material from king
        king = self.get_king()
        ks, kcom = unwrap(king.refresh_reconstruct(wrap(None)))

        # Retrieve refresh randomness from storage.

        rs = self.refresh_shares.pop(0) 
        rcom = self.new_refresh_coms.pop(0)

        new_share, new_com = dpss.refresh_postprocessing(self.pk, ks, kcom, rs, rcom)

        # Store new secret
        self.share = new_share
        self.com = new_com

        return wrap(None)

    ''' Reconstruct '''

    def update_application_state(self, request, context=None):

        state, pi = unwrap(request)
        self.application.handle_update(state, pi)


    def get_share(self, request, context=None):

        pi = unwrap(request)

        if not self.application.handle_release(pi):
            return wrap(None)
        
        if not self.share:
            raise Exception('Node ' + str(self.u) + ' does not have requested share')
        else:
            return wrap((self.share, self.com))


    def ping(self, request, context):
        print(type(request))
        a = unwrap(request)
        return wrap(sampleGF())

def serve(addr, nid, config, loop=True):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2048))
    services_pb2_grpc.add_NodeServicer_to_server(Node(addr, nid, config), server)
    print("Starting node on addr %s" % addr)
    server.add_insecure_port(addr)
    server.start()

    # Since server.start() will not block, add a sleep loop 
    if loop:
        try:
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            server.stop(0)
    else:
        return server

        
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Node")
    parser.add_argument('-a', '--addr', action='store', required=True, 
        help="This node's IP/hostname:port")
    parser.add_argument('-i', '--index', action='store', required=True, 
        help="This node's index")
    
    args = parser.parse_args()

    serve(args.addr, args.index, (params.old_addrs, params.new_addrs))



    



        

    

        

        

        

        

        
        
        
        

    

    
    


                
        
            
            
    

        





