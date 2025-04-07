import grpc
import json

from lib.logger import Logger
import lib.functions as helpers
from lib.shape_client import ShapeClient
from lib.get_method_choice import get_method_choice

def main(logger, config, methods):
    # Create the gRPC channel
    logger.info("Creating gRPC channel...")

    client: ShapeClient = ShapeClient(config, logger)

    # Create Console App
    app(methods, client)

def app(methods, client: ShapeClient):
    print('Welcome to the gRPC Console Client!')

    get_method_choice(methods, client)

if __name__ == "__main__":
    # Setup Configuration and Logging
    client_config = helpers.get_config()

    client_logger = Logger(client_config)
    helpers.log_config(client_logger, client_config)

    # client_methods = [client_config['gRPC_methods'][key] for key in client_config['gRPC_methods']]

    # Start App
    main(client_logger, client_config, client_config['gRPC_methods'])