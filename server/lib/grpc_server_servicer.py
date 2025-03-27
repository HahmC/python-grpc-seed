import os
import json
import grpc

import lib.functions as helpers
import proto.grpc_server_pb2 as grpc_server
import proto.grpc_server_pb2_grpc as grpc_service

class GrpcServerServicer(grpc_service.GrpcServerServicer):
    """
    GRPC Server Servicer - gRPC server serving all the methods defined in proto/grpc_server.proto
    """

    def __init__(self, logger, db_path, shape_limits):
        self.logger = logger
        self.db_path = db_path
        self.max_height = shape_limits['max_height']
        self.max_width = shape_limits['max_width']

        # If database .json exists use that file, otherwise create a new one
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

        shape: grpc_server.Shape = None

        if request.shape_type == "Triangle":
            self.logger.info("Generating Triangle...")

            # Generate Triangle
            shape = helpers.get_triangle(len(self.data["Triangles"]), self.max_width, self.max_height)
            shape_json: object = helpers.get_shape_json(shape)
            self.data["Triangles"].extend([shape_json])

            self.logger.info(f"Triangle: {shape}")

        elif request.shape_type == "Rectangle":
            self.logger.info("Generating Rectangle...")

            # Generate Rectangle
            shape = helpers.get_rectangle(len(self.data["Rectangles"]), self.max_width, self.max_height)
            shape_json: object = helpers.get_shape_json(shape)
            self.data["Rectangles"].extend([shape_json])

            self.logger.info(f"Rectangle: {shape}")

        elif request.shape_type == "Pentagon":
            self.logger.info("Generating Pentagon...")

            # Generate Pentagon
            shape = helpers.get_pentagon(len(self.data["Pentagons"]), self.max_width, self.max_height)
            shape_json: object = helpers.get_shape_json(shape)
            self.data["Pentagon"].extend([shape_json])

            self.logger.info(f"Pentagon: {shape}")

        else:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"shape_type {request.shape_type} is not supported at this time")

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