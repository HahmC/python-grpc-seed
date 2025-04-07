import grpc
import asyncio
from concurrent import futures

from lib.logger import Logger
import lib.functions as helpers
from lib.shape_server import ShapeServer
import shape_service_pb2_grpc as ShapeServiceGrpc

async def serve(logger, config):
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=int(config['general']['max_threads'])))
    ShapeServiceGrpc.add_ShapeServiceServicer_to_server(ShapeServer(logger, server_config['general']['json_path'], server_config['shape']), server)
    server.add_insecure_port(f"{config['general']['grpc_host']}:{config['general']['grpc_port']}")

    # Start Async Server
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    # Setup Configuration and Logging
    server_config = helpers.get_config()

    server_logger = Logger(server_config)
    helpers.log_config(server_logger, server_config)

    # Start Server
    asyncio.run(serve(server_logger, server_config))