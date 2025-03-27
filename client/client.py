import grpc

from lib.logger import Logger
import lib.functions as helpers
import proto.grpc_server_pb2_grpc as grpc_service
from lib.get_method_choice import get_method_choice

def main(logger, config, methods):
    # Create the gRPC channel
    logger.info("Creating gRPC channel...")
    channel = grpc.insecure_channel(f"{config['general']['grpc_host']}:{config['general']['grpc_port']}")
    stub = grpc_service.GrpcServerStub(channel)
    logger.info(f"Created gRPC channel to {config['general']['grpc_host']}:{config['general']['grpc_port']}")

    # Create Console App
    app(methods, stub)

def app(methods, stub):
    print('Welcome to the gRPC Console Client!')

    get_method_choice(methods, stub)

if __name__ == "__main__":
    # Setup Configuration and Logging
    client_config = helpers.get_config()

    client_logger = Logger(client_config)
    helpers.log_config(client_logger, client_config)

    client_methods = [client_config['gRPC_methods'][key] for key in client_config['gRPC_methods']]

    # Start App
    main(client_logger, client_config, client_methods)