import grpc
import threading
from time import sleep
from concurrent import futures
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from ..objects.logger import Logger

def _toggle_health(health_servicer: health.HealthServicer, service: str, logger: Logger):
    next_status = health_pb2.HealthCheckResponse.SERVING
    while True:
        # Here is where you would implement calls to databases or other external services and based on
        # their availability you could derive the health-check for the ShapeService
        logger.info(f"Health Status: {health_pb2.HealthCheckResponse.ServingStatus.Name(next_status)}")
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
        sleep(5)


def configure_health_server(server: grpc.aio.Server, logger: Logger):
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