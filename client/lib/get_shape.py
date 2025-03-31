import grpc

import proto.grpc_server_pb2 as grpc_server
import proto.grpc_server_pb2_grpc as grpc_service

def get_shape(stub: grpc_service.GrpcServerStub):
    """
    Invoces the GetShape gRPC method
    
    :param methods: list of available gRPC methods, only used to callback to main menu
    :param stub: gRPC stub to invoke method
    :return: None
    """

    print("Which shape would you like to retrieve? Enter - X to return to home menu\nshape_id format is the first letter of the shape_type followed by the shape number:")
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
        get_shape(stub)

    # Validate shape_id format
    if shape_id[1] is not '-' or int(shape_id[2:]) < 0:
        print(f"{shape_id} is not a valid shape_id")
        print()
        get_shape(stub)

    # Reformat shape_id into what the server expects
    shape_id = f"{shape_id[0].upper()}-{int(shape_id[2:])}"

    try:
        shape = stub.GetShape(grpc_server.ShapeId(shape_id=shape_id), wait_for_ready=True)

        print("Shape Retrieved:")
        print(f"shape_id: {shape.shape_id}")
        print(f"shape_type: {shape.shape_type}")
        print("coords: [")

        for c in shape.coords:
            coord_string = "{" + f"x: {c.x}, y: {c.y}" + "}"
            print(coord_string)

        print("]")

    except grpc.RpcError as e:
        print("Shape was not retrieved")
        print(f"Failed execute on server: {e.code()} - {e.details()}")

        print()
        print()
        get_shape(stub)