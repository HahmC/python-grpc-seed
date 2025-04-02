import grpc
from typing import List

import proto.grpc_server_pb2 as GrpcServer
import proto.grpc_server_pb2_grpc as GrpcService

def create_shape(methods: List[str], stub: GrpcService.GrpcServerStub):
    """
    Invokes the CreateShape gRPC method

    :param methods: list of available gRPC methods, only used to callback to main menu
    :param stub: gRPC stub to invoke method
    :return: None
    """

    print('Which type of shape would you like to create:\n[T] - Triangle\n[R] - Rectangle\n[P] - Pentagon\n[X] - Return to main menu')

    shape_choice = input('Enter the shape you would like to create: ')
    shape_choice = shape_choice.upper()

    response: GrpcServer.CreateShapeResponse = GrpcServer.CreateShapeResponse()

    try:
        if shape_choice == 'T':
            response = stub.CreateShape(GrpcServer.ShapeType(shape_type="Triangle"), wait_for_ready=True)
        elif shape_choice == 'R':
            response = stub.CreateShape(GrpcServer.ShapeType(shape_type="Rectangle"), wait_for_ready=True)
        elif shape_choice == 'P':
            response = stub.CreateShape(GrpcServer.ShapeType(shape_type="Pentagon"), wait_for_ready=True)
        elif shape_choice == 'X':
            print()
            print()
            return
        else:
            print(f"{shape_choice} is an invalid shape. Please choose a valid shape.")
            print()
            create_shape(methods, stub)

        print(f"StatusCode.{GrpcServer.Code.Name(response.status_code)} - {response.message}")

    except grpc.RpcError as e:
        print("Shape was not created")
        print(f"{e.code()} - {e.details()}")

        print()
        print()
        create_shape(methods, stub)


