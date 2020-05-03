
import grpc
import timeit
import argparse

import services_pb2
import services_pb2_grpc

def timer(func):
    def wrapper(*args, **kwargs):
        number = 100
        result = timeit.timeit(lambda: func(*args, *kwargs), number=number)
        name = str(func.__name__)
        print(name + ": " +  str(result / float(number)))
        return result
    return wrapper


def call(stub, count):
    my_ball = services_pb2.Ball(count=count)
    ball = stub.Ping(my_ball)
    return ball.count


@timer
def test_one_ball(stub, ball):
    new_ball = stub.Ping(ball)

def play(server):
    channel = grpc.insecure_channel('%s:50051' % server)
    stub = services_pb2_grpc.PingServiceStub(channel)

    count = 0
    end = False
    while not end:
        print("Ping: %d" % count)
        new_count = call(stub, count)
        print("Got: %d" % new_count)
        if not new_count == count + 1:
            end = True
        else:
            count = new_count

def test(server):
    channel = grpc.insecure_channel('%s:50051' % server)
    stub = services_pb2_grpc.PingServiceStub(channel)

    
    ball = services_pb2.Ball(count=0)
    test_one_ball(stub, ball)

if __name__ == '__main__':
    #logging.basicConfig()

    parser = argparse.ArgumentParser(description="Ping client")
    parser.add_argument('-s', '--server', action='store', required=True, 
                        help="Server's IP/hostname")
    args = parser.parse_args()

    #play(args.server)
    test(args.server)
