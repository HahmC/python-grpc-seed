import os
import grpc
import json
import time
import uuid
from configparser import ConfigParser
from typing import Iterator, List
from grpc_health.v1 import health_pb2 as HealthService
from grpc_health.v1 import health_pb2_grpc as HealthServiceGrpc

from .objects.logger import Logger
from .functions import credentials
from .gateways.auth_gateway import AuthGateway
import shape_service_pb2 as ShapeService
import shape_service_pb2_grpc as ShapeServiceGrpc


class ShapeClient:
    """
    Shape Client - gRPC client serving all the methods defined in proto/shape_service.proto
    """
    def __init__(self, config: ConfigParser, logger: Logger):
        self.logger: Logger = logger
        self.service_name: str = config['general']['service_name']
        self.max_healthcheck_attempts: int = int(config['health']['max_healthcheck_attempts'])
        self.server_host: str = config['general']['grpc_host']
        self.server_port: str = config['general']['grpc_port']

        ROOT_CERTIFICATE = credentials.load_credential_from_file(config['general']['root_certificate'])

        # Setup gRPC Channel

        # Attach credentials to every call to they can be authenticated server-side via expected header-value pair
        call_credential = grpc.metadata_call_credentials(
            AuthGateway(config['general']['signature_header'], config['general']['signature_value']), name="auth gateway"
        )

        channel_credential = grpc.ssl_channel_credentials(
            ROOT_CERTIFICATE
        )

        self.credentials = grpc.composite_channel_credentials(
            channel_credential,
            call_credential
        )

        service_config_path: str = config['general']['grpc_client_config']
        self.service_config: dict = {}

        # Load in the grpc config JSON if it exists, otherwise throw an error
        if os.path.exists(service_config_path):
            try:
                with open(service_config_path, 'r') as config_json:
                    self.service_config = json.load(config_json)
            except IOError as e:
                logger.error(f"Could not load json file: {e}")
                raise e
        else:
            raise ValueError(f"{service_config_path} does not exist")

        self.channel: grpc.aio.Channel = grpc.aio.secure_channel(
            f"{self.server_host}:{self.server_port}",
            credentials=self.credentials,
            options=[
                ("grpc.service_config", json.dumps(self.service_config))
            ]
        )

        # Setup gRPC Stub
        self.stub: ShapeServiceGrpc.ShapeServiceStub  = ShapeServiceGrpc.ShapeServiceStub(self.channel)
        self.health_stub: HealthServiceGrpc.HealthStub = HealthServiceGrpc.HealthStub(self.channel)

    async def get_shape(self):
        """
        Invokes the GetShape gRPC method

        :return: None
        """

        print(
            "Which shape would you like to retrieve? Enter - X to return to home menu\nshape_id format is the first letter of the shape_type followed by the shape number:")
        print("T-2 - Retrieves the Triangle with shape_id=T-2")
        print("R-3 - Retrieves the Rectangle with the shape_id=R-3")
        print("P-4 - Retrieves the Pentagon with the shape_id=P-4")
        print()

        shape_id = input('Enter the shape_id you would like to retrieve: ')

        # Return to main menu
        if shape_id.upper() == 'X':
            print()
            print()
            return

        # Validate that id ends with an integer
        try:
            int(shape_id[2:])
        except ValueError:
            print(f"{shape_id} is not a valid shape_id")
            print()
            return

        # Validate shape_id format
        if shape_id[1] != '-' or int(shape_id[2:]) < 0:
            print(f"{shape_id} is not a valid shape_id")
            print()
            return

        # Reformat shape_id into what the server expects
        shape_id = f"{shape_id[0].upper()}-{int(shape_id[2:])}"

        # Check service health and do not continue if the server is not healthy
        corr_id: str = str(uuid.uuid4())
        server_healthy: bool = await self.__check_server_health(0, corr_id)
        if not server_healthy:
            print("Unable to reach server")
            return

        try:
            response: ShapeService.GetShapeResponse = await self.stub.GetShape(
                ShapeService.ShapeId(shape_id=shape_id),
                wait_for_ready=True, # Wait for server to be ready
                timeout=25, # Manually override the timeout set in the grpc_client_config.json
                metadata=(
                    ("x-correlation-id", corr_id),
                    ("x-method-type", "unary-unary")
                )
            )

            print(f"StatusCode.{ShapeService.Code.Name(response.status_code)} - {response.message}")

            if response.status_code == ShapeService.Code.OK:
                print(f"shape_id: {response.shape.shape_id}")
                print(f"shape_type: {response.shape.shape_type}")
                print("coords: [")

                for c in response.shape.coords:
                    coord_string = "{" + f"x: {c.x}, y: {c.y}" + "}"
                    print(coord_string)

                print("]")

        except grpc.RpcError as e:
            print("Shape was not retrieved")
            print(f"Failed execute on server: {e.code()} - {e.details()}")

            print()
            print()
            return

    async def create_shape(self):
        """
        Invokes the CreateShape gRPC method

        :return: None
        """

        print(
            'Which type of shape would you like to create:\n[T] - Triangle\n[R] - Rectangle\n[P] - Pentagon\n[X] - Return to main menu')

        shape_choice = input('Enter the shape you would like to create: ')
        shape_choice = shape_choice.upper()

        corr_id: str = str(uuid.uuid4())
        response: ShapeService.CreateShapeResponse = None
        request_metadata = (
            ("x-correlation-id", corr_id),
            ("x-method-type", "unary-unary")
        )

        # Check service health and do not continue if the server is not healthy
        server_healthy: bool = await self.__check_server_health(0, corr_id)
        if not server_healthy:
            print("Unable to reach server")
            return

        try:
            if shape_choice == 'T':
                response = await self.stub.CreateShape(
                    ShapeService.ShapeType(shape_type="Triangle"),
                    wait_for_ready=True,  # Wait for server connection
                    metadata=request_metadata
                )
            elif shape_choice == 'R':
                response = await self.stub.CreateShape(
                    ShapeService.ShapeType(shape_type="Rectangle"),
                    wait_for_ready=True,  # Wait for server connection
                    metadata=request_metadata
                )
            elif shape_choice == 'P':
                response = await self.stub.CreateShape(
                    ShapeService.ShapeType(shape_type="Pentagon"),
                    wait_for_ready=True, # Wait for server connection
                    metadata=request_metadata
                )
            elif shape_choice == 'X':
                print()
                print()
                return
            else:
                print(f"{shape_choice} is an invalid shape. Please choose a valid shape.")
                print()
                return

            print(f"StatusCode.{ShapeService.Code.Name(response.status_code)} - {response.message}")

        except grpc.RpcError as e:
            print("Shape was not created")
            print(f"{e.code()} - {e.details()}")

            print()
            print()
            return

    async def get_total_area(self):
        """
        Gets the total area of the provided shape ids

        :return: None
        """

        print(
            "This method provides the total combined area of all the provided shape_ids. Enter X to return to the main menu")
        print("Please provide a comma separated list of all the shape_ids you wish to retrieve")
        print("Shape_id format is: T-1, R-23, ....")

        shape_ids_input = input('Enter the shape_ids you wish to have the combined areas of: ')
        shape_ids: List[str] = [shape_id.strip() for shape_id in shape_ids_input.split(',')]
        formatted_ids: List[str] = []

        # Return to main menu
        if shape_ids[0].upper() == 'X':
            print()
            print()
            return

        # Validate and reformat each of the provided shape_ids
        for shape_id in shape_ids:
            # Validate that id ends with an integer
            try:
                int(shape_id[2:])
            except ValueError:
                print(f"{shape_id} is not a valid shape_id")
                print()
                return

            # Validate shape_id format
            if shape_id[1] != '-' or int(shape_id[2:]) < 0:
                print(f"{shape_id} is not a valid shape_id")
                print()
                return

            # Reformat shape_id into what the server expects
            formatted_ids.append(f"{shape_id[0].upper()}-{int(shape_id[2:])}")

        id_iterator: Iterator[ShapeService.ShapeId] = self.__get_shape_id_iterator(formatted_ids)

        # Check service health and do not continue if the server is not healthy
        corr_id: str = str(uuid.uuid4())
        server_healthy: bool = await self.__check_server_health(0, corr_id)
        if not server_healthy:
            print("Unable to reach server")
            return

        try:
            response: ShapeService.GetTotalAreaResponse = await self.stub.GetTotalArea(
                id_iterator,
                wait_for_ready=True, # Wait for server availability
                timeout=10, # Method timeout in seconds
                metadata=(
                    ("x-correlation-id", corr_id),
                    ("x-method-type", "stream-unary")
                )
            )

            print(f"StatusCode.{ShapeService.Code.Name(response.status_code)} - {response.message}")

            if response.status_code == ShapeService.Code.OK:
                print(f"total_area: {response.total_area}")
                print(f"valid_ids: {response.valid_ids}")
                print(f"invalid_ids: {response.invalid_ids}")
            elif response.status_code == ShapeService.Code.AREA_NOT_FOUND:
                print(f"total_area: {response.total_area}")
                print(f"invalid_ids: {response.invalid_ids}")

        except grpc.RpcError as e:
            print("Shape was not retrieved")
            print(f"Failed execute on server: {e.code()} - {e.details()}")

            print()
            print()
            return

    async def get_perimeters_greater_than(self):
        """
        Invokes the GetShape gRPC method

        :return: None
        """

        print("What is the minimum perimeter to retrieve? Enter - X to return to home menu")
        print()

        min_perimeter = input('Enter the minimum perimeter to retrieve: ')

        # Return to main menu
        if min_perimeter.upper() == 'X':
            print()
            print()
            return

        # Validate that id ends with an integer
        try:
            min_perimeter = round(float(min_perimeter), 2)
        except ValueError:
            print(f"{min_perimeter} is not a valid min_perimeter")
            print()
            return

        # Check service health and do not continue if the server is not healthy
        corr_id: str = str(uuid.uuid4())
        server_healthy: bool = await self.__check_server_health(0, corr_id)
        if not server_healthy:
            print("Unable to reach server")
            return

        try:
            response: Iterator[ShapeService.GetPermitersGreaterThanResponse] = await self.stub.GetPerimetersGreaterThan(
                ShapeService.MinPerimeter(min_perimeter=min_perimeter),
                wait_for_ready=True, # Wait for server connectivity
                timeout=10, # Method timeout in seconds
                metadata=(
                    ("x-correlation-id", corr_id),
                    ("x-method-type", "unary-stream")
                )
            )

            shapes: List[ShapeService.Shape] = []

            # Iterate over the provided responses and handle them appropriately
            for r in response:
                print(f"StatusCode.{ShapeService.Code.Name(r.status_code)} - {r.message}")

                # Add the shapes to a list of shapes with perimeters above the provided value
                if r.status_code == ShapeService.Code.OK:
                    shapes.append(r.shape)


        except grpc.RpcError as e:
            print("Shape was not retrieved")
            print(f"Failed execute on server: {e.code()} - {e.details()}")

            print()
            print()

    async def get_areas(self):
        """
        Gets the individual area and shape of each of the provided shape_ids

        :return: None
        """

        print("This method retrieves the area and shape all the provided shape_ids. Enter X to return to the main menu")
        print("Please provide a comma separated list of all the shape_ids you wish to retrieve")
        print("Shape_id format is: T-1, R-23, ....")

        shape_ids_input = input('Enter the shape_ids you wish to have the areas of: ')
        shape_ids: List[str] = [shape_id.strip() for shape_id in shape_ids_input.split(',')]
        formatted_ids: List[str] = []

        # Return to main menu
        if shape_ids[0].upper() == 'X':
            print()
            print()
            return

        # Validate and reformat each of the provided shape_ids
        for shape_id in shape_ids:
            # Validate that id ends with an integer
            try:
                int(shape_id[2:])
            except ValueError:
                print(f"{shape_id} is not a valid shape_id")
                print()
                return

            # Validate shape_id format
            if shape_id[1] != '-' or int(shape_id[2:]) < 0:
                print(f"{shape_id} is not a valid shape_id")
                print()
                return

            # Reformat shape_id into what the server expects
            formatted_ids.append(f"{shape_id[0].upper()}-{int(shape_id[2:])}")

        id_iterator: Iterator[ShapeService.ShapeId] = self.__get_shape_id_iterator(formatted_ids)
        shapes_and_areas: List[tuple] = []

        # Check service health and do not continue if the server is not healthy
        corr_id: str = str(uuid.uuid4())
        server_healthy: bool = await self.__check_server_health(0, corr_id)
        if not server_healthy:
            print("Unable to reach server")
            return

        try:
            response: Iterator[ShapeService.GetAreasResponse] = await self.stub.GetAreas(
                id_iterator,
                wait_for_ready=True, # Wait for server connectivity
                timeout=10, # Method timeout
                metadata=(
                    ("x-correlation-id", corr_id),
                    ("x-method-type", "stream-stream")
                )
            )

            for r in response:
                print(f"StatusCode.{ShapeService.Code.Name(r.status_code)} - {r.message}")

                if r.status_code == ShapeService.Code.OK:
                    shapes_and_areas.append((r.shape, r.area))

        except grpc.RpcError as e:
            print("Shape was not retrieved")
            print(f"Failed execute on server: {e.code()} - {e.details()}")

            print()
            print()
            return

    @staticmethod
    def __get_shape_id_iterator(self, shape_ids: List[str]) -> Iterator[ShapeService.ShapeId]:
        """
        Creates an iterator from the provided list to pass to the grpc server stub

        :param shape_ids: list of ids to turn to an iterator
        :return: Iterator[GrpcServer.ShapeId]
        """
        for shape_id in shape_ids:
            yield ShapeService.ShapeId(shape_id=shape_id)
            time.sleep(0.5)  # Add in time-delay so user can see the operation of the iterator server-side

    async def __check_server_health(self, hc_counter: int, corr_id: str) -> bool:
        """
        Checks the health and availability of the server

        :return: bool - True if healthy, False otherwise
        """
        request: HealthService.HealthCheckRequest = HealthService.HealthCheckRequest(service="ShapeService")

        try:
            response: HealthService.HealthCheckResponse = await self.health_stub.Check(
                request,
                timeout=5,
                metadata=(
                    ('x-correlation-id', corr_id),
                    ('x-method-type', 'unary-unary'),
                )
            )

            if response.status is HealthService.HealthCheckResponse.SERVING:
                # Reset failed health check counter
                return True
            elif hc_counter % 2 == 0 and hc_counter < self.max_healthcheck_attempts:

                # Reset channel and stubs and increment counter
                hc_counter  += 1

                await self.channel.close()

                self.channel: grpc.Channel = grpc.aio.secure_channel(
                    f"{self.server_host}:{self.server_port}",
                    credentials=self.credentials,
                    options=[
                        ("grpc.service_config", json.dumps(self.service_config))
                    ]
                )

                self.stub: ShapeServiceGrpc.ShapeServiceStub = ShapeServiceGrpc.ShapeServiceStub(self.channel)
                self.health_stub: HealthServiceGrpc.HealthStub = HealthServiceGrpc.HealthStub(self.channel)

                return await self.__check_server_health(hc_counter, corr_id)

            elif hc_counter < self.max_healthcheck_attempts:
                # Increment Consecutive failed Health Checks and try again
                hc_counter += 1
                return await self.__check_server_health(hc_counter, corr_id)
            else:
                return False

        except grpc.aio.AioRpcError as e:
            if hc_counter < self.max_healthcheck_attempts:
                if e.code() is grpc.StatusCode.UNAVAILABLE or e.code() is grpc.StatusCode.DEADLINE_EXCEEDED or e.code() is grpc.StatusCode.UNKNOWN:
                    # Increment counter and try again
                    hc_counter += 1
                    return await self.__check_server_health(hc_counter, corr_id)
                else:
                    return False
            else:
                return False

