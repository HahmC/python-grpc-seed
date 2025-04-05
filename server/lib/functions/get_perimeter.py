import math

import grpc_server_pb2 as GrpcServer

def get_perimeter(shape: GrpcServer.Shape) -> float :
    """
    Calculates the perimeter of the given shape

    :param shape: shape to calculate the perimeter of
    :return: float - the perimeter of the provided shape
    """
    perimeter: float = 0.0

    n: int = len(shape.coords) # Number of coordinates in the shape

    # Calculate the distance between each set of points and add them up. i+1 % n connects the first point back to the last point
    for i in range (n):
        x_sq_diff: float = (shape.coords[(i+1) % n].x - shape.coords[i].x)**2
        y_sq_diff: float = (shape.coords[(i+1) % n].y - shape.coords[i].y)**2

        perimeter += math.sqrt( x_sq_diff + y_sq_diff )

    return perimeter
