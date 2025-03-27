import grpc
from concurrent import futures

from lib.logger import Logger
import lib.functions as helpers
import proto.grpc_server_pb2_grpc as grpc_service
from lib.grpc_server_servicer import GrpcServerServicer

def serve(logger, config):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_service.add_GrpcServerServicer_to_server(GrpcServerServicer(logger, server_config['general']['json_path'], server_config['shape']), server)
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