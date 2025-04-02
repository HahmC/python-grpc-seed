import random
from typing import List

import proto.grpc_server_pb2 as GrpcServer

def get_rectangle(rectangle_id, max_width, max_height) -> GrpcServer.Shape:
    """
    Generates a rectangle with a random width and height

    :param rectangle_id: id number for the rectangle
    :param max_width: half of the max width of the rectangle
    :param max_height: the maximum height of the rectangle
    :return: GrpcServer.Shape that is a rectangle
    """
    width: int = random.randint(1, max_width) # double the height to make division easy for middle point
    height: int = random.randint(1, max_height)

    coordinates: List[GrpcServer.ShapeCoord] = [
        GrpcServer.ShapeCoord(x=0, y=0),
        GrpcServer.ShapeCoord(x=0, y=height),
        GrpcServer.ShapeCoord(x=width, y=height),
        GrpcServer.ShapeCoord(x=width, y=0)
    ]

    rectangle: GrpcServer.Shape = GrpcServer.Shape(
        shape_id=f"R-{str(rectangle_id)}",
        shape_type="rectangle"
    )
    rectangle.coords.extend(coordinates)

    return rectangle