import sys
sys.path.append('../src/')


import params
import Pyro4.naming

Pyro4.config.THREADPOOL_SIZE = params.THREADPOOL_SIZE
Pyro4.naming.startNSloop(host=params.NSHOST, port=params.NSPORT)
