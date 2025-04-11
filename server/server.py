import grpc
import asyncio
import contextvars
from concurrent import futures

import lib.functions as helpers
from lib.objects.logger import Logger
import lib.interceptors as interceptors
import shape_service_pb2_grpc as ShapeServiceGrpc
from lib.services.shape_service import ShapeServer
from lib.services.health_check_service import configure_health_server

async def serve(logger, config):

    # Load in SSL Credentials
    server_cert = helpers.credentials.load_credential_from_file(config['general']['server_certificate'])
    server_key = helpers.credentials.load_credential_from_file(config['general']['server_key'])

    # Create server and bind interceptors
    signature_interceptor = interceptors.SignatureValidationInterceptor(
                sig_header=config['general']['signature_header'],
                sig_value=config['general']['signature_value']
    )

    # When adding interceptors to the server, remember that they are evaluated in the order that they are added
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=int(config['general']['max_threads'])),
        interceptors=(
            signature_interceptor,
        ),
    )

    # Add GRPC Service to Server
    ShapeServiceGrpc.add_ShapeServiceServicer_to_server(ShapeServer(logger, config), server)

    # Attach Credentials to Server
    server_credentials = grpc.ssl_server_credentials(
        (
            (
                server_key,
                server_cert,
            ),
        )
    )

    server.add_secure_port(
        address=f"{config['general']['grpc_host']}:{config['general']['grpc_port']}",
        server_credentials=server_credentials
    )

    # Add Health Check Service
    configure_health_server(server, logger)

    # Start Async Server
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    # Setup Configuration and Logging
    server_config = helpers.get_config()

    correlation_id = contextvars.ContextVar('correlation_id', default='')

    server_logger = Logger(server_config, correlation_id)
    helpers.log_config(server_logger, server_config)

    # Start Server
    asyncio.run(serve(server_logger, server_config))