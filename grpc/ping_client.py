
import grpc

import services_pb2
import services_pb2_grpc

def call(stub, count):
    my_ball = services_pb2.Ball(count=count)
    print("Ping: %d" % my_ball.count)
    ball = stub.Ping(my_ball)
    print("Got: %d" % ball.count)
    return ball.count

def play():
    channel = grpc.insecure_channel('localhost:50051')
    stub = services_pb2_grpc.PingServiceStub(channel)

    count = 0
    end = False
    while not end:
        new_count = call(stub, count)
        if not new_count == count + 1:
            end = True
        else:
            count = new_count

if __name__ == '__main__':
    #logging.basicConfig()
    play()
