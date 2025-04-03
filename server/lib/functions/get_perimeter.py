import math

import grpc_server_pb2 as GrpcServer

def get_perimeter(shape: GrpcServer.Shape) -> float :
    perimeter: float = 0.0

    for i in range (1, len(shape.coords)):
        x_sq_diff: float = (shape.coords[i].x - shape.coords[i-1].x)**2
        y_sq_diff: float = (shape.coords[i].y - shape.coords[i-1].y)**2

        perimeter += math.sqrt( x_sq_diff + y_sq_diff )

    # Get the distance between the first and last points in the list
    perimeter += math.sqrt( (shape.coords[0].x - shape.coords[len(shape.coords)-1].x)**2 + (shape.coords[0].y - shape.coords[len(shape.coords)-1].y)**2 )

    return perimeter
