import grpc
from typing import Iterator, List

import grpc_server_pb2 as GrpcServer
import grpc_server_pb2_grpc as GrpcService
import lib.functions as helpers


def get_areas(stub: GrpcService.GrpcServerStub):
    """
    Gets the individual area and shape of each of the provided shape_ids

    :param stub: gRPC stub to invoke method
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

    id_iterator: Iterator[GrpcServer.ShapeId] = helpers.get_shape_id_iterator(formatted_ids)
    shapes_and_areas: List[tuple] = []

    try:
        response: Iterator[GrpcServer.GetAreasResponse] = stub.GetAreas(id_iterator, wait_for_ready=True)

        for r in response:
            print(f"StatusCode.{GrpcServer.Code.Name(r.status_code)} - {r.message}")

            if r.status_code == GrpcServer.Code.OK:
                shapes_and_areas.append((r.shape, r.area))

    except grpc.RpcError as e:
        print("Shape was not retrieved")
        print(f"Failed execute on server: {e.code()} - {e.details()}")

        print()
        print()
        return