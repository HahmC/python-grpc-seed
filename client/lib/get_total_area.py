import grpc
from typing import Iterator, List

import grpc_server_pb2 as GrpcServer
import grpc_server_pb2_grpc as GrpcService
import lib.functions as helpers


def get_total_area(stub: GrpcService.GrpcServerStub):
    """
    Gets the total area of the provided shape ids

    :param stub: gRPC stub to invoke method
    :return: None
    """

    print("This method provides the total combined area of all the provided shape_ids. Enter X to return to the main menu")
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
        if shape_id[1] is not '-' or int(shape_id[2:]) < 0:
            print(f"{shape_id} is not a valid shape_id")
            print()
            return

        # Reformat shape_id into what the server expects
        formatted_ids.append(f"{shape_id[0].upper()}-{int(shape_id[2:])}")

    id_iterator: Iterator[GrpcServer.ShapeId] = helpers.get_shape_id_iterator(formatted_ids)

    try:
        response: GrpcServer.GetShapeResponse = stub.GetTotalArea(id_iterator, wait_for_ready=True)

        print(f"StatusCode.{GrpcServer.Code.Name(response.status_code)} - {response.message}")

        if response.status_code == GrpcServer.Code.OK:
            print(f"total_area: {response.total_area}")
            print(f"valid_ids: {response.valid_ids}")
            print(f"invalid_ids: {response.invalid_ids}")
        elif response.status_code == GrpcServer.Code.AREA_NOT_FOUND:
            print(f"total_area: {response.total_area}")
            print(f"invalid_ids: {response.invalid_ids}")

    except grpc.RpcError as e:
        print("Shape was not retrieved")
        print(f"Failed execute on server: {e.code()} - {e.details()}")

        print()
        print()
        return