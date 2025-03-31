import grpc
import json

from lib.logger import Logger
import lib.functions as helpers
import proto.grpc_server_pb2_grpc as grpc_service
from lib.get_method_choice import get_method_choice

def main(logger, config, methods):
    # Create the gRPC channel
    logger.info("Creating gRPC channel...")

    client_options = helpers.get_grpc_config(config['general']['grpc_client_config'])

    channel = grpc.insecure_channel(
        f"{config['general']['grpc_host']}:{config['general']['grpc_port']}",
        options=[
            ("grpc.service_config", json.dumps(client_options))
        ]
    )

    stub = grpc_service.GrpcServerStub(channel)

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