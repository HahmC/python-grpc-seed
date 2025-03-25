from concurrent import futures
import grpc

import proto.grpc_server_pb2 as grpc_server
import proto.grpc_server_pb2_grpc as grpc_service
from lib.logger import Logger
import lib.functions as helpers

class GrpcServerServicer(grpc_service.GrpcServerServicer):

    def __init__(self, logger):
        self.logger = logger
        pass

    def CreateShape(self, request: grpc_server.ShapeType, context) -> grpc_server.Shape:
        print(request)
        return grpc_server.Shape(
            shape_id=1,
            shape_type="Rectangle",
            coords=[
                grpc_server.ShapeCoord(x=0, y=0),
                grpc_server.ShapeCoord(x=0, y=1),
                grpc_server.ShapeCoord(x=1, y=1),
                grpc_server.ShapeCoord(x=1, y=0)
            ]
        )

    def GetShape(self, request: grpc_server.ShapeId, context) -> grpc_server.Shape:
        pass

def serve(logger, config):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_service.add_GrpcServerServicer_to_server(GrpcServerServicer(logger), server)
    server.add_insecure_port(f"{config['general']['grpc_host']}:{config['general']['grpc_port']}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    # Setup Configuration and Logging
    server_config = helpers.get_config()

    server_logger = Logger(server_config)
    helpers.log_config(server_logger, server_config)

    # Start Server
    serve(server_logger, server_config)