''' Application describes the generic application '''

from gfec import *
import hashlib


class Application():

    
    def __init__(self):
        return None

    ''' Initalize '''

    def create_statement(self):
        return None

    ''' Node Side '''

    # def on_initalize(u):
    #     return True

    # def handle_share(u):
    #     return True

    def handle_update(state, pi):
        return True

    def handle_release(pi):
        return True


    ''' Client Side '''
    
    # def request_share(u):
    #     return True

    def request_update(w):
        return None

    def request_release(w):
        return None

    


class Schnorr(Application):

    ''' State '''

    statement = None

    ''' Initalize '''

    # Auto-generate a statement, witness pair for testing
    def create_statement(self):
        witness = sampleGF()
        self.statement = g1 * witness
        return witness

    ''' Helper Methods '''

    def fs_challenge(self, t):
        t.normalize()
        a = hashlib.sha256(str(t).encode())
        return GF(int(a.hexdigest(), 16))

    def prove(self, witness):

        r = sampleGF()
        t = g1 * r
        c = self.fs_challenge(t)
        s = r + c * witness

        return (t, s)

    def verify(self, proof):

        t, s = proof
        c = self.fs_challenge(t)

        return g1 * s == t + self.statement * c

    ''' Application Wrappers '''


    def request_release(self, w):
        return self.prove(w)

    def handle_release(self, pi):
        return self.verify(pi)

from datetime import datetime, timedelta
import pytz
    
class TimeLock(Application):

    ''' State '''

    statement = None

    ''' Initalize '''

    # Auto-generate an unlock time for testing
    def create_statement(self, delta=None):

        if not delta:
            # Release secret one minute into the future
            delta = timedelta(seconds=60)

        self.statement = datetime.now() + delta

        # No witness needed
        return None


    ''' Application Wrappers '''

    def request_release(self, w):

        # No witness needed
        return None

    def handle_release(self, pi):

        # Standardize timezone
        ctime = pytz.utc.localize(datetime.now())
        stime = pytz.utc.localize(self.statement)

        if ctime >= stime:
            return True
        else:
            return False

import time

if __name__ == '__main__':

    timelock = TimeLock()

    statement = timelock.create_statement()

    print(statement)

    time.sleep(2)

    new_time = datetime.now()

    print(new_time)

    delta = new_time - statement

    print(abs(delta))
    print(delta)

    print(abs(delta) == abs(delta))
    print(delta == abs(delta))


    
    


