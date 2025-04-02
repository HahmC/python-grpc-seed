import grpc

import proto.grpc_server_pb2 as GrpcServer
import proto.grpc_server_pb2_grpc as GrpcService

def get_shape(stub: GrpcService.GrpcServerStub):
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
        response: GrpcServer.GetShapeResponse = stub.GetShape(GrpcServer.ShapeId(shape_id=shape_id), wait_for_ready=True)

        print(f"StatusCode.{GrpcServer.Code.Name(response.status_code)} - {response.message}")

        if response.status_code == GrpcServer.Code.OK:
            print(f"shape_id: {response.shape.shape_id}")
            print(f"shape_type: {response.shape.shape_type}")
            print("coords: [")

            for c in response.shape.coords:
                coord_string = "{" + f"x: {c.x}, y: {c.y}" + "}"
                print(coord_string)

            print("]")

        # If a shape is not found, prompt the user for a different shape_id to lookup
        elif response.status_code == GrpcServer.Code.SHAPE_NOT_FOUND:
            print()
            print()
            get_shape(stub)


    except grpc.RpcError as e:
        print("Shape was not retrieved")
        print(f"Failed execute on server: {e.code()} - {e.details()}")

        print()
        print()
        get_shape(stub)