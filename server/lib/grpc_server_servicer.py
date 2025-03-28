import os
import json
import grpc

import lib.functions as helpers
import proto.grpc_server_pb2 as grpc_server
import proto.grpc_server_pb2_grpc as grpc_service
from .logger import Logger

class GrpcServerServicer(grpc_service.GrpcServerServicer):
    """
    GRPC Server Servicer - gRPC server serving all the methods defined in proto/grpc_server.proto
    """

    def __init__(self, logger, db_path, shape_limits):
        self.logger: Logger = logger
        self.db_path: str = db_path
        self.max_height: int = int(shape_limits['max_height'])
        self.max_width: int = int(shape_limits['max_width'])

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

        :param request: The type of shape to create
        :param context: context to support error codes
        :return: The shape that was created
        """
        self.logger.info(f"CreateShape called with request: {request}")

        # Initialize with generic shape
        shape: grpc_server.Shape = grpc_server.Shape()

        if request.shape_type == "Triangle":
            self.logger.info("Generating Triangle...")

            # Generate Triangle
            shape = helpers.get_triangle(len(self.data["Triangles"]), self.max_width, self.max_height)
            shape_json: object = helpers.get_json_from_shape(shape)
            self.data["Triangles"].extend([shape_json])

            self.logger.info(f"Triangle: {shape}")

        elif request.shape_type == "Rectangle":
            self.logger.info("Generating Rectangle...")

            # Generate Rectangle
            shape = helpers.get_rectangle(len(self.data["Rectangles"]), self.max_width, self.max_height)
            shape_json: object = helpers.get_json_from_shape(shape)
            self.data["Rectangles"].extend([shape_json])

            self.logger.info(f"Rectangle: {shape}")

        elif request.shape_type == "Pentagon":
            self.logger.info("Generating Pentagon...")

            # Generate Pentagon
            shape = helpers.get_pentagon(len(self.data["Pentagons"]), self.max_width, self.max_height)
            shape_json: object = helpers.get_json_from_shape(shape)
            self.data["Pentagons"].extend([shape_json])

            self.logger.info(f"Pentagon: {shape}")

        else:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"shape_type {request.shape_type} is not supported at this time")

        # Write data back to db file
        try:
            with open(self.db_path, 'w') as json_file:
                json.dump(self.data, json_file, indent=4)
            self.logger.info(f"Data successfully written to {self.db_path}")
        except IOError as e:
            self.logger.error(f"Error writing to file: {e}")

        return shape

    def GetShape(self, request: grpc_server.ShapeId, context) -> grpc_server.Shape:
        """
        Retrieves the requested shape from the database using the shape_id and returns it to the user if present,
        otherwise throws

        :param request: gRPC Request containing the id to lookup
        :param context:
        :return: Shape corresponding to the ID requested by the user
        """
        self.logger.info(f"GetShape called with request: {request}")

        shape_id: str = f"{request.shape_id[0].upper()}{request.shape_id[1:]}" # Reformat shape_id

        shape: grpc_server.Shape = grpc_server.Shape()

        # Iterate through database looking for the given shape id
        if shape_id[0] == "T":
            for t in self.data["Triangles"]:
                if t['shape_id'] == shape_id:
                    shape = helpers.get_shape_from_json(t)
        elif shape_id[0] == "R":
            for t in self.data["Rectangles"]:
                if t['shape_id'] == shape_id:
                    shape = helpers.get_shape_from_json(t)
        elif shape_id[0] == "P":
            for t in self.data["Pentagons"]:
                if t['shape_id'] == shape_id:
                    shape = helpers.get_shape_from_json(t)
        else:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"shape_id {request.shape_id} is not a valid shape_id")

        if shape.shape_id is not '':
            return shape
        else:
            context.abort(grpc.StatusCode.NOT_FOUND, f"shape_id {request.shape_id} not found in database")