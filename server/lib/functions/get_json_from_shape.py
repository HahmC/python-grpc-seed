from typing import List

import proto.grpc_server_pb2 as grpc_server

def get_json_from_shape(shape: grpc_server.Shape) -> object:
    """
    Takes a gRCP server Shape and returns a serializable object

    :param shape: gRPC Shape
    :return: serializable object
    """
    shape_json: object = {
        "shape_id": shape.shape_id,
        "shape_type": shape.shape_type,
        "coords": []
    }

    json_coords: List[object] = []

    for c in shape.coords:
        json_coords.append({
            "x": c.x,
            "y": c.y
        })

    shape_json["coords"].extend(json_coords)

    return shape_json