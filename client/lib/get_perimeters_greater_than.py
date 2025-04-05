import grpc
from typing import Iterator, List

import grpc_server_pb2 as GrpcServer
import grpc_server_pb2_grpc as GrpcService


def get_perimeters_greater_than(stub: GrpcService.GrpcServerStub):
    """
    Invoces the GetShape gRPC method

    :param methods: list of available gRPC methods, only used to callback to main menu
    :param stub: gRPC stub to invoke method
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

    try:
        response: Iterator[GrpcServer.GetPerimetersGreaterThanResponse] = stub.GetPerimetersGreaterThan(GrpcServer.MinPerimeter(min_perimeter=min_perimeter), wait_for_ready=True)

        shapes: List[GrpcServer.Shape] = []

        # Iterate over the provided responses and handle them appropriately
        for r in response:
            print(f"StatusCode.{GrpcServer.Code.Name(r.status_code)} - {r.message}")

            # Add the shapes to a list of shapes with perimeters above the provided value
            if r.status_code == GrpcServer.Code.OK:
                shapes.append(r.shape)


    except grpc.RpcError as e:
        print("Shape was not retrieved")
        print(f"Failed execute on server: {e.code()} - {e.details()}")

        print()
        print()
        get_perimeters_greater_than(stub)