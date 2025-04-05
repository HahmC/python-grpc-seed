from typing import Iterator, List
import time

import grpc_server_pb2 as GrpcServer

def get_shape_id_iterator(shape_ids: List[str]) -> Iterator[GrpcServer.ShapeId]:
    """
    Creates an iterator from the provided list to pass to the grpc server stub

    :param shape_ids: list of ids to turn to an iterator
    :return: Iterator[GrpcServer.ShapeId]
    """
    for shape_id in shape_ids:
        yield GrpcServer.ShapeId(shape_id=shape_id)
        time.sleep(0.5) # Add in time-delay so user can see the operation of the iterator server-side