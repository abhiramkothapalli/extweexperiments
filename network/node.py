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
            print('Generating lock for function: ' + key)
            args[0].locks[key] = Lock()

        args[0].locks[key].acquire()
        try:
            if key not in args[0].cached:
                res = func(*args, **kwargs)
                args[0].cached[key] = res
        except Exception as e:
            print(e)
        args[0].locks[key].release()
                
        return wrap(args[0].cached[key])
            
    return wrapper
    

class Node(Wrapper):

    def create_locks(self):

        self.locks['refresh_reconstruct'] = Lock()
        self.locks['release_share'] = Lock()
        self.locks['distribution_verification_1'] = Lock()
        self.locks['setup_distribution_verification'] = Lock()
        

    def __init__(self, addr, nid, config):

        # Secret Share
        self.shares = []
        self.commitments = []

        self.applications = {}
        self.rcoms = []
        self.tcoms = []

        # Application to secret
        self.app_to_secret = {}

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
        self.create_locks()

        old_addrs = config[0]
        new_addrs = config[1]

        self.nid = int(nid)
        self.addr = addr

        super().__init__(old_addrs, new_addrs)

    def flush(self):

        # Secret Share
        self.shares = []
        self.commitments = []

        # Application to secret
        self.app_to_secret = {}

        # Setup Randomness
        self.setup_shares = []
        self.setup_coms = []

        # Refresh Randomness and Commitments
        self.refresh_shares = []
        self.old_refresh_coms = []
        self.new_refresh_coms = []

        self.cached = {}
        self.distributed = {}

        self.applications = {}
        self.rcoms = []
        self.tcoms = []

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
            print("Ran out of setup shares. Generating more.")
            # reset cache
            self.cached = {}
            self.distributed = {}
            self.generate_setup_randomness(None, None)



        # Pick out a setup randomness key
        rs = self.setup_shares.pop(0)
        com = self.setup_coms.pop(0)

        self.rs_temp = rs # TODO: Handle multiple shares
        self.com_temp = com # TODO: Handle multiple shares

        return wrap((rs, com))


    def handle_share_response(self, request, context):

        srzu, i = unwrap(request)
        s, r = srzu
        share, com = dpss.setup_fresh_parties(self.pk, s, r, self.rs_temp, self.com_temp)

        self.shares += [share] 
        self.commitments += [com]

        j = len(self.shares) - 1 # Identifier for the secret just added

        # Point secret to desired app
        if i not in self.app_to_secret:
            self.app_to_secret[i] = set()

        self.app_to_secret[i].update([j])
        

        return wrap(None)

    # This should only be polled from a trusted party such as the bulletin board
    def set_application(self, request, context):

        app, i = unwrap(request)

        self.applications[i] = app
        
        #self.applications += [unwrap(request)] # Handling multiple applications
        
        #return wrap(len(self.applications) - 1) # Return index of application
        return wrap(None)

    # This should only be polled from a trusted third party such as the bulletin board
    def add_application_secrets(self, request, context):

        i, indices = unwrap(request)

        # Point secret to desired app
        if i not in self.app_to_secret:
            self.app_to_secret[i] = set()

        self.app_to_secret[i].update(indices)


        return wrap(None)



    

    ''' Refresh '''


    def get_king(self):
        # CONFIGURE: In practice, the king will change each round.
        return self.old_nodes[0]


    @cache
    def release_share(self, request, context):

        shares = []
        while self.shares:

            if not self.refresh_shares:
                print('Ran out of refresh shares. Generating more.')
                # reset cache
                self.cached = {}
                self.distributed = {}
                self.generate_refresh_randomness(None, None)

            share = self.shares.pop(0)
            com = self.commitments.pop(0)

            # Refresh Randomness
            rs = self.refresh_shares.pop(0)
            rcom = self.old_refresh_coms.pop(0)

            self.tcoms += [com] # temporary commitment storage for king
            self.rcoms += [rcom]

            share, com = dpss.refresh_preprocessing(share, com, rs, rcom) # TODO make multiple shares

            shares += [share]

        return shares


    @cache
    def refresh_reconstruct(self, request, context):

        request_shares = [n.release_share.future(wrap(None)) for n in self.old_nodes]
        shares = [unwrap(s.result()) for s in request_shares]


        kpis = []
        kcoms = []
        for i in range(len(shares[0])):

            com = self.tcoms[i]
            rcom = self.rcoms[i]

            kcom = com + rcom

            ss = [share[i] for share in shares]
            kpi = dpss.refresh_king(self.pk, ss, kcom)

            kpis += [kpi]
            kcoms += [kcom]

        return (kpis, kcoms)




    def refresh(self, request, context):

        king = self.get_king()

        # Get material from king
        king = self.get_king()
        kss, kcoms = unwrap(king.refresh_reconstruct(wrap(None)))

        new_shares = []
        new_coms = []

        for i in range(len(kss)):

            # If no setup randomness available
            # then generate more.
            if not self.refresh_shares:
                print('Ran out of refresh shares. Generating more. (In refresh)')
                # reset cache
                self.cached = {}
                self.distributed = {}
                # Generate new batch of refresh shares
                self.generate_refresh_randomness(None, None)

            # Retrieve refresh randomness from storage.
            rs = self.refresh_shares.pop(0) 
            rcom = self.new_refresh_coms.pop(0)

            new_share, new_com = dpss.refresh_postprocessing(self.pk, kss[i], kcoms[i], rs, rcom)

            new_shares += [new_share]
            new_coms += [new_com]

        # Store new secret
        self.shares += new_shares
        self.commitments += new_coms




        return wrap(None)

    ''' Reconstruct '''

    def update_application_state(self, request, context=None):

        state, pi, i = unwrap(request)

        # Let application decide if state is allowed to be updated
        self.applications[i].handle_update(pi, state)

        return wrap(None)


    def get_share(self, request, context=None):

        pi, i = unwrap(request)

        if not self.applications[i].handle_release(pi):
            print('Application did not accept release')
            return wrap(None)
        
        if i not in self.app_to_secret:
            raise Exception('Requested application does not have any secrets: ' + str(i))
        else:
            secret_indices = self.app_to_secret[i]
            res = []
            for j in secret_indices:
                res += [(self.shares[j], self.commitments[j])]
            #return wrap((self.shares[i], self.commitments[i]))
            return wrap(res)


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



    



        

    

        

        

        

        

        
        
        
        

    

    
    


                
        
            
            
    

        





