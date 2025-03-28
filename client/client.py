import grpc
import json

from lib.logger import Logger
import lib.functions as helpers
import proto.grpc_server_pb2_grpc as grpc_service
from lib.get_method_choice import get_method_choice

def main(logger, config, methods):
    # Create the gRPC channel
    logger.info("Creating gRPC channel...")

    client_options = {
        "methodConfig": [
            {
                "name": [
                    {
                        "service": "proto.grpc_server_pb2_grpc.GrpcServer"
                    }
                ],
                "retryPolicy": {
                    "maxAttempts": 15,
                    "initialBackoff": "0.1s",
                    "maxBackoff": "2s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": ["UNAVAILABLE", "DEADLINE_EXCEEDED"]
                }
            }
        ]
    }

    channel = grpc.insecure_channel(
        f"{config['general']['grpc_host']}:{config['general']['grpc_port']}"
        # options=[
        #     ("grpc.service_config", json.dumps(client_options)),
        #     ("grpc.enable_retries", 1),
        #     ("grpc.keepalive_time_ms", 10000)
        # ]
    )

    # Wait for the channel to be ready
    try:
        grpc.channel_ready_future(channel).result(timeout=10)  # Wait up to 10 seconds
        print("Channel is ready!")
    except grpc.FutureTimeoutError:
        print("Error: Channel not ready within the specified timeout.")

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