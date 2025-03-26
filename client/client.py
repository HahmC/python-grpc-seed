import grpc

import proto.grpc_server_pb2_grpc as grpc_service
import proto.grpc_server_pb2 as grpc_server
from lib.logger import Logger
import lib.functions as helpers

def main(logger, config):
    # Create the gRPC channel
    logger.info("Creating gRPC channel...")
    channel = grpc.insecure_channel(f"{config['general']['grpc_host']}:{config['general']['grpc_port']}")
    stub = grpc_service.GrpcServerStub(channel)
    logger.info(f"Created gRPC channel to {config['general']['grpc_host']}:{config['general']['grpc_port']}")

    # Create Console App
    app(logger, config, stub)

def app(logger, config, stub):
    print('Welcome to the gRPC Console Client!')
    print('Available Methods: [C]reateShape [G]etShape')

    get_choice(logger, stub)

def get_choice(logger, stub):
    fxn: str = input('Enter the method you would like to use: ')
    fxn = fxn.upper()
    logger.info(f"User input: {fxn}")

    if fxn == 'C':
        logger.info("Invoking CreateShape")
        create_shape(logger, stub)
    elif fxn == "G":
        logger.info("Invoking GetShape")
    else:
        logger.info("Invalid function provided")
        print("Please Choose a valid function:\n[C] - CreateShape\n[G] - GetShape")
        print()
        get_choice(logger, stub)

def create_shape(logger, stub):
    response: grpc_server.Shape = stub.CreateShape(grpc_server.ShapeType(shape_type="Rectangle"))
    logger.info(f"Received response: {response}")

if __name__ == "__main__":
    # Setup Configuration and Logging
    client_config = helpers.get_config()

    client_logger = Logger(client_config)
    helpers.log_config(client_logger, client_config)

    # Start App
    main(client_logger, client_config)