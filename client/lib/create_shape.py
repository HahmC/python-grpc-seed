import grpc
from typing import List

import proto.grpc_server_pb2 as grpc_server
import proto.grpc_server_pb2_grpc as grpc_service

def create_shape(methods: List[str], stub: grpc_service.GrpcServerStub):
    """
    Invokes the CreateShape gRPC method

    :param methods: list of available gRPC methods, only used to callback to main menu
    :param stub: gRPC stub to invoke method
    :return: None
    """

    print('Which type of shape would you like to create:\n[T] - Triangle\n[R] - Rectangle\n[P] - Pentagon\n[X] - Return to main menu')

    shape_choice = input('Enter the shape you would like to create: ')
    shape_choice = shape_choice.upper()

    shape: grpc_server.Shape = grpc_server.Shape()

    try:
        if shape_choice == 'T':
            shape = stub.CreateShape(grpc_server.ShapeType(shape_type="Triangle"), wait_for_ready=True)
        elif shape_choice == 'R':
            shape = stub.CreateShape(grpc_server.ShapeType(shape_type="Rectangle"), wait_for_ready=True)
        elif shape_choice == 'P':
            shape = stub.CreateShape(grpc_server.ShapeType(shape_type="Pentagon"), wait_for_ready=True)
        elif shape_choice == 'X':
            print()
            print()
            return
        else:
            print(f"{shape_choice} is an invalid shape. Please choose a valid shape.")
            print()
            create_shape(methods, stub)

        if shape.shape_id is '':
            print("Shape was not created")
        else:
            print(f"You created a shape of type {shape.shape_type} and and id of {shape.shape_id}")

    except grpc.RpcError as e:
        print("Shape was not created")
        print(f"Failed execute on server: {e.code()} - {e.details()}")

        print()
        print()
        create_shape(methods, stub)


