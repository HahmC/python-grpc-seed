import random
from typing import List

import proto.grpc_server_pb2 as grpc_server

def get_pentagon(pentagon_id, max_width, max_height) -> grpc_server.Shape:
    """
    Generates a pentagon with a random width and height

    :param pentagon_id: id number for the pentagon
    :param max_width: half of the max width of the pentagon
    :param max_height: the maximum height of the pentagon
    :return: grpc_server.Shape that is a pentagon
    """
    width: int = 2*random.randint(1, max_width) # double the width to make division easy for middle point
    height: int = 2*random.randint(1, max_height) # double the height to make integer division easier for middle height

    coordinates: List[grpc_server.ShapeCoord] = [
        grpc_server.ShapeCoord(x=0, y=0),
        grpc_server.ShapeCoord(x=0, y=int(height/2)),
        grpc_server.ShapeCoord(x=int(width/2), y=height),
        grpc_server.ShapeCoord(x=width, y=int(height/2)),
        grpc_server.ShapeCoord(x=width, y=0)
    ]

    pentagon: grpc_server.Shape = grpc_server.Shape(
        shape_id=f"P-{str(pentagon_id)}",
        shape_type="pentagon"
    )
    pentagon.coords.extend(coordinates)

    return pentagon