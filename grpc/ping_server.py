from concurrent import futures
import time
import math
import logging

import grpc

# Import the generated classes
import services_pb2       # Messages
import services_pb2_grpc  # Services

class PingServicer(services_pb2_grpc.PingServiceServicer):
    def Ping(self, request, context):
        if request.count < 10:
            answer = request.count + 1
        else:
            answer = 400
        print("Pong: %d" % answer)
        return services_pb2.Ball(count=answer)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    services_pb2_grpc.add_PingServiceServicer_to_server(PingServicer(), server)
    print("Starting server on port 50051")
    server.add_insecure_port('[::]:50051')
    server.start()

    # Since server.start() will not block, add a sleep loop 
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    #logging.basicConfig()
    serve()
