import grpc
import asyncio
import threading
import contextvars
from time import sleep
from concurrent import futures
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from lib.logger import Logger
import lib.functions as helpers
from lib.shape_server import ShapeServer
import shape_service_pb2_grpc as ShapeServiceGrpc
from lib.signature_validation_interceptor import SignatureValidationInterceptor

# TODO: Add HealthChecks
# TODO: More interceptors?

def _toggle_health(health_servicer: health.HealthServicer, service: str, logger: Logger):
    next_status = health_pb2.HealthCheckResponse.SERVING
    while True:
        # Here is where you would implement calls to databases or other external services and based on
        # their availability you could derive the health-check for the ShapeService
        logger.info(f"Health Status: {health_pb2.HealthCheckResponse.ServingStatus.Name(next_status)}")
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
        sleep(5)


def _configure_health_server(server: grpc.aio.Server, logger: Logger):
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    # Use a daemon thread to toggle health status
    toggle_health_status_thread = threading.Thread(
        target=_toggle_health,
        args=(health_servicer, "ShapeService", logger),
        daemon=True,
    )
    toggle_health_status_thread.start()

async def serve(logger, config):

    # Load in SSL Credentials
    server_cert = helpers.credentials._load_credential_from_file(config['general']['server_certificate'])
    server_key = helpers.credentials._load_credential_from_file(config['general']['server_key'])

    # Create server and bind interceptors
    signature_interceptor = SignatureValidationInterceptor(
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
    _configure_health_server(server, logger)

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