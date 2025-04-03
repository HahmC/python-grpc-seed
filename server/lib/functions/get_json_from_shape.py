from typing import List

import grpc_server_pb2 as GrpcServer

def get_json_from_shape(shape: GrpcServer.Shape) -> dict:
    """
    Takes a gRCP server Shape and returns a serializable object

    :param shape: gRPC Shape
    :return: serializable object
    """
    shape_json: dict = {
        "shape_id": shape.shape_id,
        "shape_type": shape.shape_type,
        "coords": []
    }

    json_coords: List[dict] = []

    for c in shape.coords:
        json_coords.append({
            "x": c.x,
            "y": c.y
        })

    shape_json["coords"].extend(json_coords)

    return shape_json