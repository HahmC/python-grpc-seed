import random
from typing import List

import proto.grpc_server_pb2 as GrpcServer

def get_triangle(triangle_id, max_width, max_height) -> GrpcServer.Shape:
    """
    Generates a triangle with a random width and height

    :param triangle_id: id number for the triangle
    :param max_width: half of the max width of the triangle
    :param max_height: the maximum height of the triangle
    :return: GrpcServer.Shape that is a triangle
    """
    width: int = 2*random.randint(1, max_width) # double the width to make division easy for middle point
    height: int = random.randint(1, max_height)

    coordinates: List[GrpcServer.ShapeCoord] = [
        GrpcServer.ShapeCoord(x=0, y=0),
        GrpcServer.ShapeCoord(x=int(width/2), y=height),
        GrpcServer.ShapeCoord(x=width, y=0)
    ]

    triangle: GrpcServer.Shape = GrpcServer.Shape(
        shape_id=f"T-{str(triangle_id)}",
        shape_type="Triangle"
    )
    triangle.coords.extend(coordinates)

    return triangle