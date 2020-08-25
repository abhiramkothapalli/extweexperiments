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

    def handle_update(pi, state=None):
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

        # Set the statement to a time in the future
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

    
class DeadMan(Application):

    ''' State '''

    lock = None
    schnorr = None
    timeout = None

    ''' Initalize '''


    # Delta signifies how long to wait before releasing secret
    def create_statement(self, timeout=None):

        if not timeout:
            # Create a default timeout of 2 minutes
            timeout = timedelta(seconds=60)

        # Store timeout
        self.timeout = timeout

        # Create timelock based on timeout
        self.lock = TimeLock()
        self.lock.create_statement(timeout)

        # Create signature scheme for updating the timeout
        self.schnorr = Schnorr()
        privkey = self.schnorr.create_statement()

        # Return the witness that can update lock
        return privkey

    ''' Application Wrappers '''


    ''' Node Side '''

    def handle_update(self, signature, state=None):

        # Check that operator with witness is requesting update
        if self.schnorr.verify(signature):

            # Add additional time
            self.lock.statement += self.timeout
        
            return True # Successfully handled update
        else:
            return False # Update handle failed

    def handle_release(self, pi):

        # Let the timelock decide if timeout has passed
        return self.lock.handle_release(pi)


    ''' Client Side '''
    
    
    def request_update(self, privkey):

        '''
        Requests to update the timeout
        '''

        # Create a signature from the privkey
        signature = self.schnorr.prove(privkey)
        return signature

    def request_release(self, w):

        '''
        In case timeout passes request to release the secret
        '''

        # No witness needed
        return None



import time


if __name__ == '__main__':

    ''' Test Timelock '''

    # import time

    # timelock = TimeLock()

    # statement = timelock.create_statement()

    # print(statement)

    # time.sleep(2)

    # new_time = datetime.now()

    # print(new_time)

    # delta = new_time - statement

    # print(abs(delta))
    # print(delta)

    # print(abs(delta) == abs(delta))
    # print(delta == abs(delta))


    ''' Test DeadMans '''

    # Basic test
    timeout = timedelta(seconds=4)
    deadman = DeadMan()
    privkey = deadman.create_statement(timeout)
    time.sleep(2)
    assert deadman.handle_release(None) == False
    time.sleep(2)
    assert deadman.handle_release(None) == True

    # Update test
    timeout = timedelta(seconds=4) # 0
    deadman = DeadMan()
    privkey = deadman.create_statement(timeout)
    time.sleep(2) # 2
    signature = deadman.request_update(privkey)
    assert deadman.handle_release(None) == False # 2
    deadman.handle_update(signature) # Should push deadline to 8
    time.sleep(2) # 4
    assert deadman.handle_release(None) == False # 2
    time.sleep(2) # 6
    assert deadman.handle_release(None) == False # 2
    time.sleep(2) # 8
    assert deadman.handle_release(None) == True # 2
    


    
    


