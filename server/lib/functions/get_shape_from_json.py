from typing import List

import proto.grpc_server_pb2 as grpc_server

def get_shape_from_json(json_shape: object) -> grpc_server.Shape:
    """
    Takes a JSON object and converts it back to a gRPC Shape

    :param json_shape: JSON object to convert back to gRPC Shape
    :return: gRPC Shape
    """
    shape: grpc_server.Shape = grpc_server.Shape(
        shape_id=json_shape['shape_id'],
        shape_type=json_shape['shape_type']
    )

    shape_coords: List[grpc_server.ShapeCoord] = []

    for c in json_shape['coords']:
        shape_coords.append(
            grpc_server.ShapeCoord(x=int(c['x']), y=int(c['y']))
        )

    shape.coords.extend(shape_coords)

    return shape