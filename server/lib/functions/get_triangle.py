import random
from typing import List

import proto.grpc_server_pb2 as grpc_server

def get_triangle(triangle_id, max_width, max_height) -> grpc_server.Shape:
    """
    Generates a triangle with a random width and height

    :param triangle_id: id number for the triangle
    :param max_width: half of the max width of the triangle
    :param max_height: the maximum height of the triangle
    :return: grpc_server.Shape that is a triangle
    """
    width: int = 2*random.randint(1, max_width) # double the width to make division easy for middle point
    height: int = random.randint(1, max_height)

    coordinates: List[grpc_server.ShapeCoord] = [
        grpc_server.ShapeCoord(x=0, y=0),
        grpc_server.ShapeCoord(x=int(width/2), y=height),
        grpc_server.ShapeCoord(x=width, y=0)
    ]

    triangle: grpc_server.Shape = grpc_server.Shape(
        shape_id=f"T-{str(triangle_id)}",
        shape_type="Triangle"
    )
    triangle.coords.extend(coordinates)

    return triangle