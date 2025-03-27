import random
from typing import List

import proto.grpc_server_pb2 as grpc_server

def get_rectangle(rectangle_id, max_width, max_height) -> grpc_server.Shape:
    """
    Generates a rectangle with a random width and height

    :param rectangle_id: id number for the rectangle
    :param max_width: half of the max width of the rectangle
    :param max_height: the maximum height of the rectangle
    :return: grpc_server.Shape that is a rectangle
    """
    width: int = random.randint(1, max_width) # double the height to make division easy for middle point
    height: int = random.randint(1, max_height)

    coordinates: List[grpc_server.ShapeCoord] = [
        grpc_server.ShapeCoord(x=0, y=0),
        grpc_server.ShapeCoord(x=0, y=height),
        grpc_server.ShapeCoord(x=width, y=height),
        grpc_server.ShapeCoord(x=width, y=0)
    ]

    rectangle: grpc_server.Shape = grpc_server.Shape(
        shape_id=f"R-{str(rectangle_id)}",
        shape_type="rectangle"
    )
    rectangle.coords.extend(coordinates)

    return rectangle