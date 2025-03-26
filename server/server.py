from concurrent import futures
import grpc
import json
import os

import proto.grpc_server_pb2 as grpc_server
import proto.grpc_server_pb2_grpc as grpc_service
from lib.logger import Logger
import lib.functions as helpers

class GrpcServerServicer(grpc_service.GrpcServerServicer):

    def __init__(self, logger, db_path):
        self.logger = logger
        self.db_path = db_path

        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as json_file:
                    self.data = json.load(json_file)
            except IOError as e:
                logger.error(f"Could not load json file: {e}")
        else:
            self.data = {"Triangles": [], "Rectangles": [], "Pentagons":[]}

    def CreateShape(self, request: grpc_server.ShapeType, context) -> grpc_server.Shape:
        """
        Create the shape specified by the user, giving it an id and coordinates
        """
        self.logger.info(f"CreateShape called with request: {request}")
        coords = [
            grpc_server.ShapeCoord(x=0, y=0),
            grpc_server.ShapeCoord(x=1, y=0),
            grpc_server.ShapeCoord(x=1, y=1),
            grpc_server.ShapeCoord(x=0, y=1)
        ]

        coords_json = [
            {"x": 0, "y": 0},
            {"x": 1, "y": 0},
            {"x": 1, "y": 1},
            {"x": 0, "y": 1}
        ]

        shape = grpc_server.Shape(
            shape_id=f"R-{len(self.data["Rectangles"])}",
            shape_type="Rectangle"
        )
        shape.coords.extend(coords)

        shape_json = {
            "shape_id": shape.shape_id,
            "shape_type": shape.shape_type,
            "coords": []
        }
        shape_json["coords"].extend(coords_json)

        self.data["Rectangles"].extend([shape_json])

        # Write data back to db file
        try:
            with open(self.db_path, 'w') as json_file:
                json.dump(self.data, json_file, indent=4)
            print(f"Data successfully written to {self.db_path}")
        except IOError as e:
            print(f"Error writing to file: {e}")

        return shape

    def GetShape(self, request: grpc_server.ShapeId, context) -> grpc_server.Shape:
        pass

def serve(logger, config):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_service.add_GrpcServerServicer_to_server(GrpcServerServicer(logger, server_config['general']['json_path']), server)
    server.add_insecure_port(f"{config['general']['grpc_host']}:{config['general']['grpc_port']}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    # Setup Configuration and Logging
    server_config = helpers.get_config()

    server_logger = Logger(server_config)
    helpers.log_config(server_logger, server_config)

    # Start Server
    serve(server_logger, server_config)