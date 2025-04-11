import asyncio

import lib.functions as helpers
from lib.objects.logger import Logger
from lib.shape_client import ShapeClient

async def main(logger, config, methods):
    # Create the gRPC channel
    logger.info("Creating gRPC channel...")

    client: ShapeClient = ShapeClient(config, logger)

    # Create Console App
    await app(methods, client)

async def app(methods, client: ShapeClient):
    print('Welcome to the gRPC Console Client!')

    await helpers.get_method_choice(methods, client)

if __name__ == "__main__":
    # Setup Configuration and Logging
    client_config = helpers.get_config()

    client_logger = Logger(client_config)
    helpers.log_config(client_logger, client_config)

    # Start App
    asyncio.run(main(client_logger, client_config, client_config['gRPC_methods']))